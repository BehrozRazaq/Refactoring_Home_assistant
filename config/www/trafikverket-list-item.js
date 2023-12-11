import {
  LitElement,
  html,
  css,
} from "https://unpkg.com/lit-element@2.0.1/lit-element.js?module";

export class ListItem extends LitElement {
  static properties = {
    src: String,
    name: String,
    quantity: Number,
    selected: Boolean,
    showOverlay: Boolean,
    hass: {},
    entryId: {},
  };

  constructor() {
    super();
    this.showOverlay = false;
  }

  static styles = css`
    .camera-list-item {
      display: flex;
      justify-content: space-between;
      border-style: solid;
      border-width: 2px 0px 0px 0px;
      border-color: #444444;
      padding: 5px;
    }
    .camera-list-item:hover {
      background-color: #666666;
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
      background: #333333 !important;
    }
    .low {
      background: #00ff00;
    }
    .medium {
      background: #ffff00;
    }
    .high {
      background: #ff0000;
    }
    .critical {
      background: #000000;
      color: #ffffff;
    }
    .unknown {
      background: #444444;
      color: #ffffff;
    }
    @media (prefers-color-scheme: dark) {
      .item-selected {
        background: #424242;
      }
    }
  `;

  handleContextMenu(e) {
    e.preventDefault();
    this.showOverlay = true;
    console.log("Right click");
  }

  handleRemove() {
    this.showOverlay = false;
    this.hass.callWS({
      type: "trafikverket_camera/remove",
      entry_id: this.entryId,
      location: this.name,
    });
  }

  render() {
    let labelClass = "";
    switch (this.quantity) {
      case 1:
        labelClass = "Low";
        break;
      case 2:
        labelClass = "Medium";
        break;
      case 3:
        labelClass = "High";
        break;
      case 4:
        labelClass = "Critical";
        break;
      default:
        labelClass = "Unknown";
        break;
    }

    let extraClass = "";
    if (this.selected) {
      extraClass = " item-selected";
    }

    return html`
      <div
        class="camera-list-item${extraClass}"
        @contextmenu="${this.handleContextMenu}"
      >
        ${this.showOverlay
          ? html`
              <div class="overlay">
                <button @click="${this.handleRemove}">Remove</button>
              </div>
            `
          : html`
              <img class="camera-preview-column" src="${this.src}" />
              <p class="camera-location-column">${this.name}</p>
              <div class="traffic-density-label ${labelClass.toLowerCase()}">
                ${labelClass}
              </div>
            `}
      </div>
    `;
  }
}

customElements.define("list-item", ListItem);
