import {
  LitElement,
  html,
  css,
} from "https://unpkg.com/lit-element@2.0.1/lit-element.js?module";

export class BigCameraView extends LitElement {
  static properties = {
    src: {},
    name: {},
    data: {},
  };

  drawRects() {
    const imageElement = this.shadowRoot.children[0].children[1].children[0];
    const canvas = this.shadowRoot.getElementById("rect-drawer");
    canvas.width = imageElement.width;
    canvas.height = imageElement.height;
    const ctx = canvas.getContext("2d");
    const image = new Image();
    const data = this.formattedData ? this.formattedData : [];
    image.onload = function () {
      const widthScale = canvas.width / image.width;
      const heightScale = canvas.height / image.height;

      for (let i = 0; i < data.length; i++) {
        const d = data[i];
        ctx.beginPath();
        ctx.rect(
          Math.round(d.x1 * widthScale),
          Math.round(d.y1 * heightScale),
          Math.round(d.x2 * widthScale),
          Math.round(d.y2 * heightScale)
        );
        ctx.strokeStyle = "#ff0000ff";
        ctx.lineWidth = 2;
        ctx.stroke();
      }
    };
    image.src = this.src;
  }

  onImageLoad() {
    this.drawRects();
  }

  connectedCallback() {
    super.connectedCallback();
    if (this.imageElement) {
      return;
    }
    this.imageElement = this.shadowRoot.getElementById("camera-large-img");
    if (this.imageElement) {
      this.imageElement.addEventListener("load", this.onImageLoad.bind(this));
    }
  }

  firstUpdated() {
    this.drawRects();
  }

  static styles = css`
    #camera-large {
      padding: 20px;
      width: inherit;
    }
    #camera-large-img {
      width: 100%;
      height: auto;
    }
    #camera-large-title {
      text-align: center;
    }
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
    #rect-drawer {
      position: absolute;
      top: 0;
      left: 0;
    }
  `;

  render() {
    if (this.data) {
      this.formattedData = JSON.parse(this.data);
    }
    const item = html`
      <div id="camera-large">
        <h3 id="camera-large-title">${this.name}</h3>
        <div style="position: relative;">
          <img id="camera-large-img" src="${this.src}" />
          <canvas id="rect-drawer" />
        </div>
      </div>
    `;
    return item;
  }
}

customElements.define("big-camera-view", BigCameraView);
