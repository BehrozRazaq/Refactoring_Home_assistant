import {
  LitElement,
  html,
  css,
} from "https://unpkg.com/lit-element@2.0.1/lit-element.js?module";

export class NavigationView extends LitElement {
  static properties = {
    mode: String,
  };

  static styles = css`
    .arrow {
      border: solid #444444;
      border-width: 0 3px 3px 0;
      display: inline-block;
      padding: 3px;
      width: 15px;
      height: 15px;
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
    #navigation-container {
      display: flex;
      justify-content: center;
    }
  `;

  render() {
    return html`
      <div id="navigation-container">
        <div class="arrow left"></div>
        <p class="mode-text">${this.mode}</p>
        <div class="arrow right"></div>
      </div>
    `;
  }
}

customElements.define("navigation-view", NavigationView);
