"""
Type definitions for the omfg-deck plugin.
"""
from typing import TypedDict, Optional, List


class InstallationResponse(TypedDict):
    success: bool
    message: str
    error: Optional[str]


class UninstallationResponse(TypedDict):
    success: bool
    message: str
    removed_files: Optional[List[str]]
    error: Optional[str]


class InstallationCheckResponse(TypedDict):
    installed: bool
    lib_exists: bool
    json_exists: bool
    lib_path: str
    json_path: str
    error: Optional[str]


class ConfigurationResponse(TypedDict):
    success: bool
    config: Optional[dict]
    message: Optional[str]
    error: Optional[str]


class UpdateCheckResponse(TypedDict):
    success: bool
    update_available: bool
    current_version: str
    latest_version: str
    release_notes: str
    release_date: str
    download_url: str
    error: Optional[str]


class UpdateDownloadResponse(TypedDict):
    success: bool
    download_path: Optional[str]
    error: Optional[str]
