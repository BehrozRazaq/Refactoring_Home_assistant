import {
  LitElement,
  html,
  css,
} from "https://unpkg.com/lit-element@2.0.1/lit-element.js?module";

export class NavigationView extends LitElement {
  static properties = {
    mode: String,
    onChange: Function,
  };

  static styles = css`
    .arrow {
      border: solid #333333;
      border-width: 0 3px 3px 0;
      display: inline-block;
      padding: 3px;
      width: 15px;
      height: 15px;
    }
    .arrow:hover {
      border-color: #555555;
    }
    .right {
      transform: rotate(-45deg);
    }
    .left {
      transform: rotate(135deg);
    }
    .mode-text {
      margin: 0px 0px 30px 0px;
    }
    .disabled {
      border-color: #999999 !important;
    }
    #navigation-container {
      display: flex;
      justify-content: center;
    }
    @media (prefers-color-scheme: dark) {
      .arrow {
        border: solid #171717;
        border-width: 0 3px 3px 0;
      }
      .disabled {
        border-color: #3c3c3c !important;
      }
    }
  `;

  render() {
    const leftArrow =
      this.mode == "Image"
        ? html`<div class="arrow left disabled" />`
        : html`<div class="arrow left" @click="${this.onChange}" />`;
    const rightArrow =
      this.mode == "Statistics"
        ? html`<div class="arrow right disabled" />`
        : html`<div class="arrow right" @click="${this.onChange}" />`;

    return html`
      <div id="navigation-container">
        ${leftArrow}
        <p class="mode-text">${this.mode}</p>
        ${rightArrow}
      </div>
    `;
  }
}

customElements.define("navigation-view", NavigationView);
