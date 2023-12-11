import {
  LitElement,
  html,
  css,
} from "https://unpkg.com/lit-element@2.0.1/lit-element.js?module";
import "https://unpkg.com/chart.js@4.2.0/dist/chart.umd.js";
import "https://cdn.jsdelivr.net/npm/chartjs-adapter-date-fns";

export class StatisticsView extends LitElement {
  static properties = {
    data: [{ location: String, time: String, nr_cars: Number }],
    name: String,
    display: String,
    chart: {},
  };

  constructor() {
    super();
    this.display = "day";
  }

  updated(updatedItems) {
    const namesOfUpdated = Array.from(updatedItems.keys());
    if (namesOfUpdated.length == 1 && namesOfUpdated[0] == "chart") {
      return;
    }
    if (this.chart) {
      this.chart.destroy();
      this.chart = undefined;
    }
    const ctx = this.shadowRoot.getElementById("statistics").getContext("2d");
    let refinedData = JSON.parse(this.data).map((d) => ({
      x: d[0],
      y: d[1],
    }));

    const timeFrames = {
      hour: 3600 * 1000,
      day: 3600 * 1000 * 24,
      week: 3600 * 1000 * 24 * 7,
      month: 3600 * 1000 * 24 * 30,
      year: 3600 * 1000 * 24 * 365,
    };

    const units = {
      hour: "minute",
      day: "hour",
      week: "day",
      month: "day",
      year: "day",
    };

    const now = new Date();
    const oldest = new Date(now.getTime() - timeFrames[this.display]);
    refinedData = refinedData.filter((d) => {
      const dataTime = new Date(d.x);
      return dataTime > oldest;
    });

    refinedData = refinedData.reduce((acc, d) => {
      let date = new Date(d.x);
      switch (this.display) {
        case "hour":
          break;
        case "day":
          date.setMinutes(Math.floor(date.getMinutes() / 30) * 30, 0, 0);
          break;
        case "week":
          date.setHours(Math.floor(date.getHours() / 4) * 4, 0, 0, 0);
          break;
        case "month":
        case "year":
          date.setHours(0, 0, 0, 0);
          break;
      }
      let time = date.toISOString();
      if (!acc[time]) {
        acc[time] = [];
      }
      acc[time].push(d.y);
      return acc;
    }, {});

    let data = [];
    for (let key in refinedData) {
      let sum = refinedData[key].reduce((a, b) => a + b, 0);
      data.push({ x: key, y: Math.round(sum / refinedData[key].length) });
    }

    console.log(data);

    this.chart = new Chart(ctx, {
      type: "line",
      data: {
        datasets: [
          {
            label: "Number of Cars",
            data: data,
            borderWidth: 1,
          },
        ],
      },
      options: {
        scales: {
          y: {
            beginAtZero: true,
          },
          x: {
            parsing: false,
            type: "time",
            time: {
              //This unit can be changed to match what we want
              unit: units[this.display],
            },
          },
        },
      },
    });
  }

  static styles = css`
    #statistics {
      width: inherit;
      padding: 20px;
    }
    #statistics-title {
      text-align: center;
    }
    #statistics-container {
      padding: 20px;
    }
  `;

  render() {
    return html` <div id="statistics-container">
      <h3 id="statistics-title">${this.name}</h3>
      <div id="statistics-buttons">
        <button
          @click="${(_) => {
            this.display = "hour";
          }}"
        >
          Hour
        </button>
        <button
          @click="${(_) => {
            this.display = "day";
          }}"
        >
          Day
        </button>
        <button
          @click="${(_) => {
            this.display = "week";
          }}"
        >
          Week
        </button>
        <button
          @click="${(_) => {
            this.display = "month";
          }}"
        >
          Month
        </button>
        <button
          @click="${(_) => {
            this.display = "year";
          }}"
        >
          Year
        </button>
      </div>
      <canvas id="statistics"></canvas>
    </div>`;
  }
}

customElements.define("statistics-view", StatisticsView);
