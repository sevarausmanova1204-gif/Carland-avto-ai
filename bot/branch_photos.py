"""Filiallarning tashqi ko'rinishi rasmlari: assets/branch_photos/<filial_id>_<n>.jpg"""
from pathlib import Path

PHOTOS_DIR = Path(__file__).resolve().parent.parent / "assets" / "branch_photos"


def get_branch_photo_paths(branch_id: int) -> list[Path]:
    return sorted(PHOTOS_DIR.glob(f"{int(branch_id)}_*.jpg"))
