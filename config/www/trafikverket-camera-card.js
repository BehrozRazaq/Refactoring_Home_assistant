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

  renderListItem(cameraData, index) {
    const imgPath = cameraData.attributes.entity_picture;
    const friendlyName = cameraData.attributes.friendly_name;
    const quantity = cameraData.attributes.traffic_quantity
      ? cameraData.attributes.traffic_quantity
      : "low";
    let labelColor;
    let labelText;
    switch (quantity) {
      case "low":
        labelColor = "#00ff00";
        labelText = "low";
        break;
      default:
        labelColor = "#ffffff";
        labelText = "SOMETHING WENT WRONG";
        break;
    }
    let extraClass = "";
    if (index == this.selectedIndex) {
      extraClass = " item-selected";
    }

    return html`
      <div
        class="camera-list-item${extraClass}"
        @click="${(_) => (this.selectedIndex = index)}"
      >
        <img class="camera-preview-column" src="${imgPath}" />
        <p class="camera-location-column">${friendlyName}</p>
        <div class="traffic-density-label" style="background: ${labelColor};">
          ${labelText}
        </div>
      </div>
    `;
  }

  renderBigView() {
    const cameraData =
      this.hass.states[this.config.cameras[this.selectedIndex]];
    const imgPath = cameraData.attributes.entity_picture;
    const friendlyName = cameraData.attributes.friendly_name;
    return html`
      <div>
        <h3>${friendlyName}</h3>
        <img class="camera-large" src="${imgPath}" />
        <div>
          <p class="arrow left" />
          <p>${this.mode}</p>
          <p class="arrow right" />
        </div>
      </div>
    `;
  }

  render() {
    return html`
      <ha-card header="Camera Card">
        <div id="camera-card-content">
          <div id="camera-list">
            <div id="camera-list-description">
              <p class="camera-preview-column">Last picture</p>
              <p class="camera-location-column">Location</p>
              <p style="margin-right: 20px;">Traffic</p>
            </div>
            <div id="camera-list-contents">
              ${this.config.cameras.map((cameraId, index) =>
                this.renderListItem(this.hass.states[cameraId], index)
              )}
            </div>
          </div>
          ${this.renderBigView()}
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
      .arrow {
        border: solid black;
        border-width: 0 3px 3px 0;
        display: inline-block;
        padding: 3px;
      }
      .right {
        transform: rotate(-45deg);
      }
      .left {
        transform: rotate(135deg);
      }
      #camera-card-content {
        display: flex;
      }
      #camera-list {
        background: #777777;
        color: #222222;
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
      .camera-large {
        width: 400px;
      }
      .camera-list-item {
        display: flex;
        justify-content: space-between;
        border-style: solid;
        border-width: 2px 0px 0px 0px;
        border-color: #444444;
        padding: 5px;
      }
      .camera-preview-column {
        width: 50px;
        height: 50px;
        text-align: center;
      }
      .camera-location-column {
        flex-grow: 2;
        padding-left: 20px;
      }
      .traffic-density-label {
        width: 50px;
        height: 20px;
        border-radius: 45px;
        align-self: center;
        margin-right: 10px;
        text-align: center;
      }
      .item-selected {
        background: #444444;
      }
    `;
  }
}

customElements.define("trafikverket-camera-card", TrafikverketCameraCard);
