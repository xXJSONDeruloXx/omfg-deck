import { useState, useEffect, useCallback } from "react";
import { toaster } from "@decky/api";
import { getWorkarounds, setWorkaround } from "../api/omfgApi";

export interface WorkaroundState {
  mesa_immediate: boolean;
  disable_vkbasalt: boolean;
  force_enable_vkbasalt: boolean;
  dxvk_frame_rate: number;
  enable_wow64: boolean;
  disable_steamdeck: boolean;
  mangohud: boolean;
  enable_gamescope_wsi: boolean;
  enable_zink: boolean;
}

const DEFAULTS: WorkaroundState = {
  mesa_immediate: false,
  disable_vkbasalt: false,
  force_enable_vkbasalt: false,
  dxvk_frame_rate: 0,
  enable_wow64: false,
  disable_steamdeck: false,
  mangohud: false,
  enable_gamescope_wsi: false,
  enable_zink: false,
};

export function useWorkarounds() {
  const [workarounds, setWorkarounds] = useState<WorkaroundState>(DEFAULTS);

  const fetchWorkarounds = useCallback(async () => {
    try {
      const r = await getWorkarounds();
      if (r.success) {
        setWorkarounds({
          mesa_immediate:        r.mesa_immediate,
          disable_vkbasalt:      r.disable_vkbasalt,
          force_enable_vkbasalt: r.force_enable_vkbasalt,
          dxvk_frame_rate:       r.dxvk_frame_rate,
          enable_wow64:          r.enable_wow64,
          disable_steamdeck:     r.disable_steamdeck,
          mangohud:              r.mangohud,
          enable_gamescope_wsi:  r.enable_gamescope_wsi,
          enable_zink:           r.enable_zink,
        });
      }
    } catch { /* keep defaults */ }
  }, []);

  /** toggle: key + boolean (booleans stored as "0"/"1") */
  const toggle = useCallback(async (key: keyof WorkaroundState, enabled: boolean) => {
    try {
      const r = await setWorkaround(key, enabled ? "1" : "0");
      if (r.success) {
        setWorkarounds((prev) => {
          const next = { ...prev, [key]: enabled };
          // Enforce mutex client-side immediately
          if (key === "disable_vkbasalt" && enabled) next.force_enable_vkbasalt = false;
          if (key === "force_enable_vkbasalt" && enabled) next.disable_vkbasalt = false;
          return next;
        });
      } else {
        toaster.toast({ title: "Workaround failed", body: r.error ?? "Unknown" });
      }
    } catch (e) {
      toaster.toast({ title: "Workaround failed", body: String(e) });
    }
  }, []);

  /** setInt: for numeric values like dxvk_frame_rate */
  const setInt = useCallback(async (key: keyof WorkaroundState, value: number) => {
    try {
      const r = await setWorkaround(key, String(value));
      if (r.success) {
        setWorkarounds((prev) => ({ ...prev, [key]: value }));
      } else {
        toaster.toast({ title: "Workaround failed", body: r.error ?? "Unknown" });
      }
    } catch (e) {
      toaster.toast({ title: "Workaround failed", body: String(e) });
    }
  }, []);

  useEffect(() => { fetchWorkarounds(); }, [fetchWorkarounds]);

  return { workarounds, toggle, setInt };
}
