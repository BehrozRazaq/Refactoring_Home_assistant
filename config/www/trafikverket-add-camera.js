import {
  LitElement,
  html,
  css,
} from "https://unpkg.com/lit-element@2.0.1/lit-element.js?module";

export class AddCamera extends LitElement {
  static properties = {};

  static styles = css``;
  static get properties() {
    return {
      items: { type: Array },
      selectedItem: { type: String },
      hass: {},
      entryId: {},
    };
  }

  constructor() {
    super();
    this.items = [];
    this.selectedItem = "";
  }

  handleSelection(e) {
    this.selectedItem = e.target.value;
  }

  handleAdd() {
    // Add your logic for adding items here
    this.hass.callWS({
      type: "trafikverket_camera/add",
      entry_id: this.entryId,
      location: this.selectedItem,
    });
  }

  getCameras() {
    if (this.items.length > 0) return;
    const waitForEntryId = () => {
      if (!this.entryId) {
        setTimeout(waitForEntryId, 50);
      } else {
        this.hass
          .callWS({
            type: "trafikverket_camera/get_cameras",
            entry_id: this.entryId,
          })
          .then((cameras) => {
            this.items = cameras;
            this.items.sort((a, b) => {
              const a_n = a.camera_name;
              const b_n = b.camera_name;
              if (a_n > b_n) return 1;
              if (a_n < b_n) return -1;
              return 0;
            });
            this.requestUpdate();
          });
      }
    };
    waitForEntryId();
  }

  firstUpdated() {
    this.getCameras();
  }

  render() {
    return html`
      <select @change="${this.handleSelection}">
        ${this.items.map(
          (item) =>
            html`<option
              value="${item.camera_name}"
              title="${item.description}"
            >
              ${item.camera_name}
            </option>`
        )}
      </select>
      <button @click="${this.handleAdd}">Add</button>
    `;
  }
}

customElements.define("add-camera", AddCamera);
