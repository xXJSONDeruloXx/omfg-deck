import React, { useState, useEffect } from "react";
import { ButtonItem, PanelSection } from "@decky/ui";
import { checkForPluginUpdate, downloadPluginUpdate, UpdateCheckResult, UpdateDownloadResult } from "../api/omfgApi";

export const PluginUpdateChecker: React.FC = () => {
  const [checking, setChecking] = useState(false);
  const [downloading, setDownloading] = useState(false);
  const [updateInfo, setUpdateInfo] = useState<UpdateCheckResult | null>(null);
  const [downloadResult, setDownloadResult] = useState<UpdateDownloadResult | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (error) {
      const t = setTimeout(() => setError(null), 5000);
      return () => clearTimeout(t);
    }
    return undefined;
  }, [error]);

  const handleCheck = async () => {
    setChecking(true);
    setError(null);
    setUpdateInfo(null);
    setDownloadResult(null);
    try {
      const result = await checkForPluginUpdate();
      if (result.success) {
        setUpdateInfo(result);
      } else {
        setError(result.error ?? "Failed to check for updates");
      }
    } catch (e) {
      setError(String(e));
    } finally {
      setChecking(false);
    }
  };

  const handleDownload = async () => {
    if (!updateInfo?.download_url) return;
    setDownloading(true);
    setError(null);
    try {
      const result = await downloadPluginUpdate(updateInfo.download_url);
      if (result.success) {
        setDownloadResult(result);
      } else {
        setError(result.error ?? "Download failed");
      }
    } catch (e) {
      setError(String(e));
    } finally {
      setDownloading(false);
    }
  };

  const statusNode = updateInfo
    ? updateInfo.update_available
      ? downloadResult?.success
        ? <div style={{ color: "lightgreen" }}>✓ v{updateInfo.latest_version} downloaded</div>
        : <div style={{ color: "orange" }}>Update available: v{updateInfo.latest_version}</div>
      : <div style={{ color: "lightgreen" }}>Up to date (v{updateInfo.current_version})</div>
    : null;

  return (
    <PanelSection title="Plugin Updates">
      <ButtonItem
        layout="below"
        onClick={handleCheck}
        disabled={checking}
        description={statusNode}
      >
        {checking ? "Checking..." : "Check for Updates"}
      </ButtonItem>

      {updateInfo?.update_available && !downloadResult?.success && (
        <ButtonItem layout="below" onClick={handleDownload} disabled={downloading}>
          {downloading ? "Downloading..." : `Download v${updateInfo.latest_version}`}
        </ButtonItem>
      )}

      {downloadResult?.success && (
        <div style={{ fontSize: "12px", marginTop: "8px", opacity: 0.85 }}>
          Saved to: {downloadResult.download_path}
          <br />
          Install via Decky Loader → Developer → Install from ZIP.
        </div>
      )}

      {error && (
        <div style={{ color: "red", fontSize: "12px", marginTop: "8px" }}>{error}</div>
      )}
    </PanelSection>
  );
};
