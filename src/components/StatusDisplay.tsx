import { PanelSectionRow } from "@decky/ui";

interface StatusDisplayProps {
  isInstalled: boolean;
  installationStatus: string;
}

export function StatusDisplay({ isInstalled, installationStatus }: StatusDisplayProps) {
  return (
    <PanelSectionRow>
      <div
        style={{
          color: isInstalled ? "#4CAF50" : "#FF9800",
          fontWeight: "600",
          display: "flex",
          alignItems: "center",
          gap: "6px",
          fontSize: "13px",
          marginBottom: "4px",
        }}
      >
        <span style={{ fontSize: "15px" }}>{isInstalled ? "✅" : "❌"}</span>
        {installationStatus}
      </div>
    </PanelSectionRow>
  );
}
