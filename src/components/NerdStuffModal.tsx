import { useState } from "react";
import { ModalRoot, Focusable } from "@decky/ui";
import { getConfigFileContent, getWrapperScriptContent } from "../api/omfgApi";

interface Props { closeModal?: () => void; }

function RawFileView({ label, content }: { label: string; content: string }) {
  const [copied, setCopied] = useState(false);

  const handleCopy = () => {
    if (navigator.clipboard) {
      navigator.clipboard.writeText(content).catch(() => {});
    } else {
      const el = document.createElement("textarea");
      el.value = content;
      el.style.position = "fixed"; el.style.opacity = "0";
      document.body.appendChild(el); el.focus(); el.select();
      document.execCommand("copy");
      document.body.removeChild(el);
    }
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <div style={{ marginBottom: "16px" }}>
      <div style={{
        display: "flex", justifyContent: "space-between", alignItems: "center",
        marginBottom: "6px",
      }}>
        <span style={{ fontWeight: "bold", fontSize: "13px" }}>{label}</span>
        <button onClick={handleCopy} style={{
          background: "rgba(255,255,255,0.12)", border: "none", borderRadius: "4px",
          color: "#fff", cursor: "pointer", padding: "3px 10px", fontSize: "12px",
        }}>
          {copied ? "✓ Copied" : "Copy"}
        </button>
      </div>
      <div style={{
        fontFamily: "monospace", fontSize: "10px", lineHeight: "1.4",
        background: "rgba(0,0,0,0.45)", border: "1px solid rgba(255,255,255,0.12)",
        borderRadius: "4px", padding: "8px", maxHeight: "200px", overflowY: "auto",
        whiteSpace: "pre-wrap", wordBreak: "break-all", color: "#a8d8a8",
      }}>
        {content || "(empty)"}
      </div>
    </div>
  );
}

export function NerdStuffModal({ closeModal }: Props) {
  const [configContent, setConfigContent] = useState<string | null>(null);
  const [wrapperContent, setWrapperContent] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const load = async () => {
    setLoading(true); setError(null);
    try {
      const [cfg, wrap] = await Promise.all([
        getConfigFileContent(),
        getWrapperScriptContent(),
      ]);
      setConfigContent(cfg.success ? cfg.content : `Error: ${cfg.error}`);
      setWrapperContent(wrap.success ? wrap.content : `Error: ${wrap.error}`);
    } catch (e) {
      setError(String(e));
    } finally {
      setLoading(false);
    }
  };

  return (
    <ModalRoot>
      <div style={{ padding: "16px", minWidth: "420px", maxWidth: "600px" }}>
        <h2 style={{ marginBottom: "12px" }}>🔧 Nerd Stuff</h2>

        {configContent === null && !loading && !error && (
          <Focusable>
            <button onClick={load} style={{
              background: "rgba(255,255,255,0.15)", border: "none", borderRadius: "6px",
              color: "#fff", cursor: "pointer", padding: "8px 20px", fontSize: "14px",
              marginBottom: "16px",
            }}>
              Load File Contents
            </button>
          </Focusable>
        )}

        {loading && <div style={{ opacity: 0.7, marginBottom: "12px" }}>Loading…</div>}
        {error && <div style={{ color: "#F44336", marginBottom: "12px" }}>{error}</div>}

        {configContent !== null && (
          <RawFileView label="omfg-live.toml" content={configContent} />
        )}
        {wrapperContent !== null && (
          <RawFileView label="omfg-wrapper.sh" content={wrapperContent} />
        )}

        <Focusable style={{ marginTop: "12px" }}>
          <button onClick={closeModal} style={{
            background: "rgba(255,255,255,0.1)", border: "none", borderRadius: "6px",
            color: "#fff", cursor: "pointer", padding: "8px 20px", fontSize: "14px",
          }}>
            Close
          </button>
        </Focusable>
      </div>
    </ModalRoot>
  );
}
