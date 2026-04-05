import { staticClasses } from "@decky/ui";
import { definePlugin } from "@decky/api";
import { FaLayerGroup } from "react-icons/fa";
import { Content } from "./components";

export default definePlugin(() => {
  console.log("omfg-deck plugin initializing");

  return {
    name: "OMFG",
    titleView: <div className={staticClasses.Title}>OMFG</div>,
    content: <Content />,
    icon: <FaLayerGroup />,
    onDismount() {
      console.log("omfg-deck unloading");
    },
  };
});
