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
  static get properties() {
    return {
      hass: {},
      config: {},
    };
  }

  renderListItem(cameraData) {
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

    return html`
      <div class="camera-list-item">
        <img class="camera-preview-column" src="${imgPath}" />
        <p class="camera-location-column">${friendlyName}</p>
        <div class="traffic-density-label" style="background: ${labelColor};">
          ${labelText}
        </div>
      </div>
    `;
  }

  render() {
    return html`
      <ha-card header="Camera Card">
        <div class="card-content">
          <div id="camera-list">
            <div id="camera-list-description">
              <p class="camera-preview-column">Last picture</p>
              <p class="camera-location-column">Location</p>
              <p style="margin-right: 20px;">Traffic</p>
            </div>
            <div id="camera-list-contents">
              ${this.config.cameras.map((cameraId) =>
                this.renderListItem(this.hass.states[cameraId])
              )}
            </div>
          </div>
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
    `;
  }
}

customElements.define("trafikverket-camera-card", TrafikverketCameraCard);
