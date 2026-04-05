import { useState } from "react";
import { PanelSectionRow, ButtonItem } from "@decky/ui";
import { FaFileAlt, FaTimes } from "react-icons/fa";
import { getLayerLog } from "../api/omfgApi";

export function LogViewer() {
  const [log, setLog] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleFetch = async () => {
    setLoading(true);
    setError(null);
    try {
      const result = await getLayerLog(60);
      if (result.success) {
        setLog(result.log || "(log file is empty)");
      } else {
        setError(result.error ?? result.message ?? "Failed to read log");
      }
    } catch (e) {
      setError(String(e));
    } finally {
      setLoading(false);
    }
  };

  return (
    <>
      <PanelSectionRow>
        <ButtonItem layout="below" onClick={log ? () => setLog(null) : handleFetch} disabled={loading}>
          <div style={{ display: "flex", alignItems: "center", gap: "8px" }}>
            {log ? <FaTimes /> : <FaFileAlt />}
            <div>{loading ? "Loading log…" : log ? "Close Log" : "View Layer Log"}</div>
          </div>
        </ButtonItem>
      </PanelSectionRow>

      {error && (
        <PanelSectionRow>
          <div style={{ fontSize: "11px", color: "#F44336", opacity: 0.9 }}>{error}</div>
        </PanelSectionRow>
      )}

      {log && (
        <PanelSectionRow>
          <div style={{
            fontFamily: "monospace",
            fontSize: "9px",
            lineHeight: "1.4",
            background: "rgba(0,0,0,0.45)",
            border: "1px solid rgba(255,255,255,0.12)",
            borderRadius: "4px",
            padding: "6px 8px",
            maxHeight: "200px",
            overflowY: "auto",
            whiteSpace: "pre-wrap",
            wordBreak: "break-all",
            color: "#c8ffc8",
          }}>
            {log}
          </div>
        </PanelSectionRow>
      )}
    </>
  );
}
