import { PanelSectionRow } from "@decky/ui";

interface StatusDisplayProps {
  isInstalled: boolean;
  installationStatus: string;
  configExists: boolean;
  wrapperExists: boolean;
}

export function StatusDisplay({
  isInstalled,
  installationStatus,
  configExists,
  wrapperExists,
}: StatusDisplayProps) {
  return (
    <PanelSectionRow>
      <div style={{ marginBottom: "6px", fontSize: "13px" }}>
        <div
          style={{
            color: isInstalled ? "#4CAF50" : "#FF9800",
            fontWeight: "600",
            display: "flex",
            alignItems: "center",
            gap: "6px",
            marginBottom: "4px",
          }}
        >
          <span style={{ fontSize: "15px" }}>{isInstalled ? "✅" : "❌"}</span>
          {installationStatus}
        </div>

        {isInstalled && (
          <>
            <div
              style={{
                color: configExists ? "#4CAF50" : "#FF9800",
                display: "flex",
                alignItems: "center",
                gap: "6px",
                marginBottom: "2px",
              }}
            >
              <span>{configExists ? "✅" : "⚠️"}</span>
              {configExists ? "Config file present" : "Config file missing"}
            </div>

            <div
              style={{
                color: wrapperExists ? "#4CAF50" : "#888",
                display: "flex",
                alignItems: "center",
                gap: "6px",
              }}
            >
              <span>{wrapperExists ? "✅" : "ℹ️"}</span>
              {wrapperExists ? "Wrapper script present" : "Wrapper script not found"}
            </div>
          </>
        )}
      </div>
    </PanelSectionRow>
  );
}
