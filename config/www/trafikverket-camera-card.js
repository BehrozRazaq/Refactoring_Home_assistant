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

import "./trafikverket-big-camera-view.js";
import "./trafikverket-list-item.js";
import "./trafikverket-navigation-view.js";
import "./trafikverket-statistics-view.js";
import "./trafikverket-add-camera.js";

class TrafikverketCameraCard extends LitElement {
  constructor() {
    super();
    this.selectedIndex = 0;
    this.mode = "Image";
    this.cameras = [];
  }

  static get properties() {
    return {
      hass: {},
      config: {},
      selectedIndex: { type: Number },
      mode: { type: String },
    };
  }

  changeMode() {
    if (this.mode == "Image") {
      this.mode = "Statistics";
    } else {
      this.mode = "Image";
    }
  }

  firstUpdated() {
    if (this.entryId) return;
    this.hass.callWS({ type: "config_entries/get" }).then((configEntries) => {
      console.log(configEntries);
      this.entryId = configEntries.filter(
        (e) => e.domain == "trafikverket_camera"
      )[0].entry_id;
      this.requestUpdate();
    });
  }

  setCameras() {
    const regex = /^camera\.trafikverket_camera.*/;
    const filteredKeys = Object.keys(this.hass.states).filter((key) =>
      regex.test(key)
    );

    this.cameras = filteredKeys.map((key) => this.hass.states[key]);
  }

  render() {
    console.log(this.hass.states);
    this.setCameras();
    if (this.cameras.length == 0) {
      return html` <add-camera
        .entryId=${this.entryId}
        .hass=${this.hass}
      ></add-camera>`;
    }
    if (this.selectedIndex >= this.cameras.length) {
      this.selectedIndex = 0;
    }
    const cameraData = this.cameras[this.selectedIndex];
    const imgPath = cameraData.attributes.entity_picture;
    const friendlyName = cameraData.attributes.friendly_name;
    const statistics = JSON.stringify(cameraData.attributes.statistics);
    const carRects = JSON.stringify(cameraData.attributes.car_rectangles);
    const infoView =
      this.mode == "Image"
        ? html`<big-camera-view
            data="${carRects}"
            name="${friendlyName}"
            src="${imgPath}"
          ></big-camera-view>`
        : html`<statistics-view
            data="${statistics}"
            name="${friendlyName}"
          ></statistics-view>`;
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
              ${this.cameras.map((data, index) => {
                const imgPath = data.attributes.entity_picture;
                const name = data.attributes.name;
                const selected = true ? index == this.selectedIndex : false;
                const quantity = data.attributes.traffic_measure;
                return html`<list-item
                  src="${imgPath}"
                  name="${name}"
                  .hass="${this.hass}"
                  .entryId="${this.entryId}"
                  quantity="${quantity}"
                  selected="${selected}"
                  @click="${(_) => {
                    this.selectedIndex = index;
                    this.mode = "Image";
                  }}"
                />`;
              })}
              <add-camera
                .entryId=${this.entryId}
                .hass=${this.hass}
              ></add-camera>
            </div>
          </div>
          <div id="info-view">
            ${infoView}
            <navigation-view
              mode="${this.mode}"
              onChange="${() => {
                this.changeMode();
              }}"
            ></navigation-view>
          </div>
        </div>
      </ha-card>
    `;
  }

  // The user supplied configuration. Throw an exception and Home Assistant
  // will render an error card.
  setConfig(config) {
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
        min-height: 450px;
        background: #dddddd;
        font-color: #212121;
      }
      #camera-list {
        background: #999999;
        color: #222222;
        margin: 20px;
        width: 33%;
        border-style: solid;
        border-width: 2px;
        border-color: #444444;
        border-radius: 10px;
        box-shadow: 2px 2px 2px 0px #606060;
      }
      #info-view {
        height: inherit;
        border-left-style: solid;
        border-width: 4px;
        border-color: #a4a4a4;
        width: 67%;
        display: flex;
        flex-direction: column;
        justify-content: space-between;
      }
      #camera-card-content {
        min-height: 450px;
        display: flex;
      }
      #camera-list-description {
        display: flex;
        justify-content: space-between;
      }
      #camera-list-description > p {
        margin: 0px;
        align-self: center;
      }
      @media (prefers-color-scheme: dark) {
        ha-card {
          font-color: #cccccc;
          background: #303030;
        }
        #camera-list {
          background: #5b5b5b;
          box-shadow: 2px 2px 4px 0px #222;
          border-color: #282828;
        }
        #info-view {
          border-color: #444444;
        }
      }
    `;
  }
}

customElements.define("trafikverket-camera-card", TrafikverketCameraCard);
