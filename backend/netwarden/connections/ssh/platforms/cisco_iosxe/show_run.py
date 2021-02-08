from typing import Dict, Any
import re


def parse_show_run(data: Dict[str, Any]) -> Dict[str, Any]:
    cfg = re.sub(r"^Building configuration.+", "", data, flags=re.M)
    cfg = re.sub(r"^Current configuration :.+", "", cfg, flags=re.M)
    cfg = re.sub(r"^\s*!\s*", "", cfg)
    cfg = cfg.strip()
    return {
        "cfg": cfg
    }
