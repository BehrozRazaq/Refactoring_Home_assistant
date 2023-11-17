/*{
  "entity_id": "camera.nyangsrondellen_nordost",
  "state": "idle",
  "attributes": {
    "access_token": "2d6eaf191738fbc8dacaaf39a974ccee15325c154c8e2530403721f0f5adf415",
    "description": "",
    "location": "Nyängsrondellen nordost",
    "type": "Trafikflödeskamera",
    "entity_picture": "/api/camera_proxy/camera.nyangsrondellen_nordost?token=2d6eaf191738fbc8dacaaf39a974ccee15325c154c8e2530403721f0f5adf415",
    "friendly_name": "Nyängsrondellen nordost",
    "supported_features": 0
  },
  "context": {
    "id": "01HF3YFMM89061K5PCJEEA35HP",
    "parent_id": null,
    "user_id": null
  },
  "last_changed": "2023-11-13T08:04:05.344Z",
  "last_updated": "2023-11-13T08:59:00.616Z"
}*/

import {
  LitElement,
  html,
  css,
} from "https://unpkg.com/lit-element@2.0.1/lit-element.js?module";

import "https://unpkg.com/chart.js@4.2.0/dist/chart.umd.js";
import "https://cdn.jsdelivr.net/npm/chartjs-adapter-date-fns";
import "./trafikverket-big-camera-view.js";
import "./trafikverket-list-item.js";
import "./trafikverket-navigation-view.js";

class TrafikverketCameraCard extends LitElement {
  constructor() {
    super();
    this.selectedIndex = 0;
    this.mode = "Image";
  }

  static get properties() {
    return {
      hass: {},
      config: {},
      selectedIndex: { type: Number },
      mode: { type: String },
    };
  }

  firstUpdated() {
    this.hass.states[this.config.cameras[this.selectedIndex]];
    //nrOfCars = cameraData.attributes.
    const ctx = this.shadowRoot.getElementById("myChart").getContext("2d");

    //const labels = utils.months;

    new Chart(ctx, {
      type: "line",
      data: {
        datasets: [
          {
            label: "Number of Cars",
            data: [
              { x: "2023-11-17T03:00:00", y: "3" },
              { x: "2023-11-17T04:00:00", y: "20" },
              { x: "2023-11-17T05:00:00", y: "21" },
              { x: "2023-11-17T06:00:00", y: "22" },
              { x: "2023-11-17T07:00:00", y: "8" },
              { x: "2023-11-17T08:00:00", y: "10" },
              { x: "2023-11-17T09:00:00", y: "15" },
              { x: "2023-11-17T10:00:00", y: "13" },
              { x: "2023-11-17T11:00:00", y: "23" },
              { x: "2023-11-17T12:00:00", y: "25" },
              { x: Date.now(), y: "5" },
            ],
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

  render() {
    const cameraData =
      this.hass.states[this.config.cameras[this.selectedIndex]];
    const imgPath = cameraData.attributes.entity_picture;
    const friendlyName = cameraData.attributes.friendly_name;
    return html`
      <ha-card>
        <div id="camera-card-content">
          <div id="camera-list">
            <div id="camera-list-description">
              <p class="camera-preview-column">Last picture</p>
              <p class="camera-location-column">Location</p>
              <p style="margin-right: 20px;">Traffic</p>
            </div>
            <div id="camera-list-contents">
              ${this.config.cameras.map((cameraId, index) => {
                const data = this.hass.states[cameraId];
                const imgPath = data.attributes.entity_picture;
                const name = data.attributes.friendly_name;
                const selected = true ? index == this.selectedIndex : false;
                const quantity = data.attributes.traffic_measure;
                return html`<list-item
                  src="${imgPath}"
                  name="${name}"
                  quantity="${quantity}"
                  selected="${selected}"
                  @click="${(_) => (this.selectedIndex = index)}"
                />`;
              })}
            </div>
          </div>
          <div>
            <big-camera-view name="${friendlyName}" src="${imgPath}">
            </big-camera-view>
            <navigation-view mode="Image"></navigation-view>
          </div>
        </div>
        <div>
          <canvas id="myChart" width="600" height="400"></canvas>
        </div>
      </ha-card>
    `;
  }

  // The user supplied configuration. Throw an exception and Home Assistant
  // will render an error card.
  setConfig(config) {
    if (!config.cameras) {
      throw new Error("Need cameras");
    }
    this.config = config;
  }

  // The height of your card. Home Assistant uses this to automatically
  // distribute all cards over the available columns.
  getCardSize() {
    return this.config.cameras.length + 1;
  }

  static get styles() {
    return css`
      ha-card {
        width: 800px;
      }
      #camera-card-content {
        display: flex;
      }
      #camera-list {
        background: #777777;
        color: #222222;
        margin: 20px;
        border-style: solid;
        border-width: 2px;
        border-color: #444444;
        border-radius: 10px;
      }
      #camera-list-description {
        display: flex;
        justify-content: space-between;
      }
      #camera-list-description > p {
        margin: 0px;
        align-self: center;
      }
      big-camera-view {
      }
    `;
  }
}

customElements.define("trafikverket-camera-card", TrafikverketCameraCard);
