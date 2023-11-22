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
  };

  firstUpdated() {
    //this.hass.states[this.config.cameras[this.selectedIndex]];
    //nrOfCars = cameraData.attributes.
    const ctx = this.shadowRoot.getElementById("statistics").getContext("2d");
    const refinedData = JSON.parse(this.data).map((d) => ({
      x: d[0],
      y: d[1],
    }));

    //const labels = utils.months;

    new Chart(ctx, {
      type: "line",
      data: {
        datasets: [
          {
            label: "Number of Cars",
            data: refinedData,
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
              unit: "hour",
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
      <canvas id="statistics"></canvas>
    </div>`;
  }
}

customElements.define("statistics-view", StatisticsView);
