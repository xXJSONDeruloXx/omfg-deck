import { PanelSectionRow, ButtonItem } from "@decky/ui";
import { FaGithub } from "react-icons/fa";

export function GitHubButton() {
  return (
    <PanelSectionRow>
      <ButtonItem
        layout="below"
        onClick={() => window.open("https://github.com/xXJSONDeruloXx/omfg", "_blank")}
      >
        <div style={{ display: "flex", alignItems: "center", gap: "8px" }}>
          <FaGithub />
          <div>OMFG on GitHub</div>
        </div>
      </ButtonItem>
    </PanelSectionRow>
  );
}
