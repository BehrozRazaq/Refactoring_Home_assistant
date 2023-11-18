import {
  LitElement,
  html,
  css,
} from "https://unpkg.com/lit-element@2.0.1/lit-element.js?module";

export class BigCameraView extends LitElement {
  static properties = {
    src: String,
    name: String,
  };

  static styles = css`
    #camera-large {
      padding: 20px;
      width: inherit;
    }
    #camera-large-img {
      width: 100%;
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
  `;

  render() {
    return html`
      <div id="camera-large">
        <h3 id="camera-large-title">${this.name}</h3>
        <img id="camera-large-img" src="${this.src}" />
      </div>
    `;
  }
}

customElements.define("big-camera-view", BigCameraView);
