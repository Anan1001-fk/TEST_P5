#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Retimer SDK Drive Python封装模块

该模块提供:
    - ctypes 结构体定义
    - `RetimerSDKDrive` 类，封装 DLL 接口

注意:
    - 依赖 `libretimer_sdk_drive.dll`/`retimer_sdk_drive.dll`
    - 若在 Windows 环境下，需要同目录下存在 `USB2UARTSPIIICDLL.dll`
"""

from __future__ import annotations

import ctypes
from ctypes import cdll
import os
import sys
from typing import Dict, Iterable, List, NamedTuple, Optional, Sequence, Tuple

__all__ = [
    "DeviceInfo",
    "PVTSensor",
    "PVTSensors",
    "SDKLink",
    "LinkStatus",
    "EyeResult",
    "RetimerSDKDrive",
    "BIF_NAMES",
    "LINK_NAMES",
    "LTSSM_NAMES",
    "SWITCH_DIAG_REG_COUNT",
    "SWITCH_DIAG_SRAM_NUM",
    "SWITCH_DIAG_SRAM_DEPTH",
    "SwitchDiagnosticianConfig",
    "SwitchDiagnosticianData",
    "SwitchDiagnostician",
]


BIF_NAMES = [
    "x16",
    "x8",
    "x4",
    "x8x8",
    "x8x4x4",
    "x4x4x8",
    "x4x4x4x4",
    "x2x2x2x2x2x2x2x2",
    "x8x4x2x2",
    "x8x2x2x4",
    "x2x2x4x8",
    "x4x2x2x8",
    "x2x2x2x2x8",
    "x8x2x2x2x2",
    "x2x2x4x4x4",
    "x4x2x2x4x4",
    "x4x4x2x2x4",
    "x4x4x4x2x2",
    "x2x2x2x2x4x4",
    "x2x2x4x2x2x4",
    "x4x2x2x2x2x4",
    "x2x2x4x4x2x2",
    "x4x2x2x4x2x2",
    "x4x4x2x2x2x2",
    "x2x2x2x2x2x2x4",
    "x2x2x2x2x4x2x2",
    "x2x2x4x2x2x2x2",
    "x4x2x2x2x2x2x2",
    "x4x4",
    "x2x2x4",
    "x4x2x2",
    "x2x2x2x2",
    "x2x2",
]

LINK_NAMES = [
    "LINK1_X16",
    "LINK2_X2_0",
    "LINK3_X4_0",
    "LINK4_X2_1",
    "LINK5_X8",
    "LINK6_X2_2",
    "LINK7_X4_1",
    "LINK8_X2_3",
]

LTSSM_NAMES = {
    0x00: "DETECT",
    0x03: "RATE CHANGE",
    0x04: "FWD FORWARDING",
    0x05: "FWD HOT RESET",
    0x06: "FWD DISABLE",
    0x07: "FWD LPBK",
    0x08: "FWD CPL RCV",
    0x09: "FWD ENTER CPL",
    0x0A: "FWD PM L1_1",
    0x10: "EXE CLB ENTRY",
    0x11: "EXE CLB PATTERN",
    0x12: "EXE CLB EXIT",
    0x14: "EXE EO PH2 ACTIVE",
    0x15: "EXE EO PH2 PASSIVE",
    0x16: "EXE EO PH3 ACTIVE",
    0x17: "EXE EO PH3 PASSIVE",
    0x18: "EXE EO FORCE TIMEOUT",
    0x1C: "EXE SLAVE LPBK ENTRY",
    0x1D: "EXE SLAVE LPBK ACTIVE",
    0x1E: "EXE SLAVE LPBK EXIT",
}

SWITCH_DIAG_REG_COUNT = 17
SWITCH_DIAG_SRAM_NUM = 18
SWITCH_DIAG_SRAM_DEPTH = 256
SWITCH_DIAG_SIG_REG_MAX = 10
SWITCH_DIAG_SIGNALS_MAX = 512


class DeviceInfo(ctypes.Structure):
    _fields_ = [
        ("type", ctypes.c_int),
        ("port", ctypes.c_int),
        ("high_speed", ctypes.c_int),
        ("status", ctypes.c_char * 256),
        ("description", ctypes.c_char * 256),
    ]


class PVTSensor(ctypes.Structure):
    _fields_ = [
        ("vol", ctypes.c_float),
        ("temp", ctypes.c_float),
        ("lvt", ctypes.c_float),
        ("ulvt", ctypes.c_float),
        ("svt", ctypes.c_float),
        ("vol_reg_data", ctypes.c_uint32),
        ("temp_reg_data", ctypes.c_uint32),
        ("lvt_reg_data", ctypes.c_uint32),
        ("ulvt_reg_data", ctypes.c_uint32),
        ("svt_reg_data", ctypes.c_uint32),
    ]


class PVTSensors(ctypes.Structure):
    _fields_ = [
        ("pvt_num", ctypes.c_int),
        ("pvt", PVTSensor * 3),
    ]


class SDKLink(ctypes.Structure):
    _fields_ = [
        ("linkup", ctypes.c_uint8),
        ("ltssm", ctypes.c_uint8),
        ("link_no", ctypes.c_uint8),
        ("width", ctypes.c_uint8),
        ("active_width", ctypes.c_uint8),
        ("downgrade", ctypes.c_uint8),
        ("debug_a_forwarding_data_os_n", ctypes.c_uint8),
        ("debug_b_forwarding_data_os_n", ctypes.c_uint8),
        ("lane_h", ctypes.c_uint8),
        ("lane_l", ctypes.c_uint8),
        ("speed", ctypes.c_int),
        ("active_lanes", ctypes.c_uint16),
        ("same_link_lanes", ctypes.c_uint16),
        ("b_rx_det_lanes", ctypes.c_uint16),
        ("a_rx_det_lanes", ctypes.c_uint16),
    ]


class LinkStatus(ctypes.Structure):
    _fields_ = [
        ("bif", ctypes.c_int),
        ("link_num", ctypes.c_int),
        ("link_is_reset", ctypes.c_int),
        ("link", SDKLink * 8),
    ]


class EyeResult(ctypes.Structure):
    _fields_ = [
        ("valid", ctypes.c_bool),
        ("right_ui", ctypes.c_double),
        ("left_ui", ctypes.c_double),
        ("top_mv", ctypes.c_double),
        ("bot_mv", ctypes.c_double),
    ]


SwitchDiagRegArray = ctypes.c_uint32 * SWITCH_DIAG_REG_COUNT
SwitchDiagSramRow = ctypes.c_uint32 * SWITCH_DIAG_SRAM_NUM
SwitchDiagSramArray = SwitchDiagSramRow * SWITCH_DIAG_SRAM_DEPTH


class SwitchDiagSramInfo(ctypes.Structure):
    _fields_ = [
        ("mode", ctypes.c_uint32),
        ("valid_depth", ctypes.c_int32),
    ]


class SwitchDiagnosticianConfig(ctypes.Structure):
    _fields_ = [
        ("port", ctypes.c_int),
        ("mode", ctypes.c_uint32),
        ("la_ctrl", ctypes.c_uint32),
        ("repeat_ctrl", ctypes.c_uint32),
        ("sam_sel", SwitchDiagRegArray),
        ("pat_sel", SwitchDiagRegArray),
        ("rtrig_sel", SwitchDiagRegArray),
        ("ftrig_sel", SwitchDiagRegArray),
    ]


class SwitchDiagnosticianData(ctypes.Structure):
    _fields_ = [
        ("info", SwitchDiagSramInfo),
        ("sram", SwitchDiagSramArray),
    ]


class _DiaSignalSegment(ctypes.Structure):
    _fields_ = [
        ("reg_no", ctypes.c_uint8),
        ("sram_no", ctypes.c_uint8),
        ("msb", ctypes.c_uint8),
        ("lsb", ctypes.c_uint8),
        ("bits", ctypes.c_uint8),
    ]


class _DiaSignal(ctypes.Structure):
    _fields_ = [
        ("signal_name", ctypes.c_char_p),
        ("total_bits", ctypes.c_uint16),
        ("reg_sram_num", ctypes.c_uint16),
        ("reg_sram", _DiaSignalSegment * SWITCH_DIAG_SIG_REG_MAX),
    ]


class _DiaSignalTable(ctypes.Structure):
    _fields_ = [
        ("sig_num", ctypes.c_int),
        ("sig", _DiaSignal * SWITCH_DIAG_SIGNALS_MAX),
    ]


class _SignalSegment(NamedTuple):
    reg_no: int
    sram_no: int
    msb: int
    lsb: int
    bits: int


class _SignalDescriptor(NamedTuple):
    total_bits: int
    segments: Tuple[_SignalSegment, ...]


class SwitchDiagnostician:
    """Switch diagnostician功能的高层封装."""

    def __init__(
        self,
        sdk: "RetimerSDKDrive",
        adapter_type: int,
        adapter_port: int,
        slave_addr: int,
        *,
        switch_port: int,
        bitrate_khz: int = 400,
        pec_enable: bool = True,
        chip_version: int = 1,
    ):
        self._sdk = sdk
        self.adapter_type = adapter_type
        self.adapter_port = adapter_port
        self.diag_port = switch_port
        self.slave_addr = slave_addr
        self._handle = self._sdk.switch_diag_open(
            adapter_type,
            adapter_port,
            slave_addr,
            bitrate_khz,
            1 if pec_enable else 0,
            chip_version,
        )

    # ------------------------------------------------------------------
    # 生命周期管理
    # ------------------------------------------------------------------
    def close(self) -> None:
        if self._handle:
            self._sdk.switch_diag_close(self._handle)
            self._handle = None

    def __del__(self):
        self.close()

    def __enter__(self) -> "SwitchDiagnostician":
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        self.close()

    # ------------------------------------------------------------------
    # 工具方法
    # ------------------------------------------------------------------
    def _ensure_handle(self):
        if not self._handle:
            raise RuntimeError("Diagnostician handle is not available (already closed)")
        return self._handle

    @staticmethod
    def _fill_config_array(target, values: Optional[Sequence[int]]):
        if not values:
            return
        for idx, value in enumerate(values[:SWITCH_DIAG_REG_COUNT]):
            target[idx] = value

    @staticmethod
    def build_config(
        port: int,
        *,
        mode: int = 0,
        la_ctrl: int = 0,
        repeat_ctrl: int = 0,
        sam_sel: Optional[Sequence[int]] = None,
        pat_sel: Optional[Sequence[int]] = None,
        rtrig_sel: Optional[Sequence[int]] = None,
        ftrig_sel: Optional[Sequence[int]] = None,
    ) -> SwitchDiagnosticianConfig:
        cfg = SwitchDiagnosticianConfig()
        cfg.port = port
        cfg.mode = mode
        cfg.la_ctrl = la_ctrl
        cfg.repeat_ctrl = repeat_ctrl
        SwitchDiagnostician._fill_config_array(cfg.sam_sel, sam_sel)
        SwitchDiagnostician._fill_config_array(cfg.pat_sel, pat_sel)
        SwitchDiagnostician._fill_config_array(cfg.rtrig_sel, rtrig_sel)
        SwitchDiagnostician._fill_config_array(cfg.ftrig_sel, ftrig_sel)
        return cfg

    @staticmethod
    def data_to_python(data: SwitchDiagnosticianData) -> dict:
        return {
            "mode": data.info.mode,
            "valid_depth": data.info.valid_depth,
            "sram": [
                [data.sram[row][col] for col in range(SWITCH_DIAG_SRAM_NUM)]
                for row in range(SWITCH_DIAG_SRAM_DEPTH)
            ],
        }

    # ------------------------------------------------------------------
    # 诊断功能
    # ------------------------------------------------------------------
    def set_address(self, slave_addr: int) -> None:
        self._sdk.switch_diag_set_address(self._ensure_handle(), slave_addr)
        self.slave_addr = slave_addr

    def clock_and_reset_check(self, port: Optional[int] = None) -> None:
        target_port = self.diag_port if port is None else port
        self._sdk.switch_diag_clock_and_reset_check(
            self._ensure_handle(),
            target_port,
        )

    def start(self, config: SwitchDiagnosticianConfig) -> None:
        self._sdk.switch_diag_start(self._ensure_handle(), config)

    def stop(self, port: Optional[int] = None) -> None:
        target_port = self.diag_port if port is None else port
        self._sdk.switch_diag_stop(self._ensure_handle(), target_port)

    def is_stop(self, port: Optional[int] = None) -> bool:
        target_port = self.diag_port if port is None else port
        return self._sdk.switch_diag_is_stop(
            self._ensure_handle(),
            target_port,
        )

    def sram_is_full(self, port: Optional[int] = None) -> bool:
        target_port = self.diag_port if port is None else port
        return self._sdk.switch_diag_sram_is_full(
            self._ensure_handle(),
            target_port,
        )

    def read_sram(
        self,
        port: Optional[int] = None,
    ) -> SwitchDiagnosticianData:
        data = SwitchDiagnosticianData()
        target_port = self.diag_port if port is None else port
        self._sdk.switch_diag_sram_read(
            self._ensure_handle(),
            target_port,
            data,
        )
        return data

    def read_sram_python(self, port: Optional[int] = None) -> dict:
        return SwitchDiagnostician.data_to_python(self.read_sram(port))

    def save_csv(
        self,
        filename: str,
        data: Optional[SwitchDiagnosticianData] = None,
    ) -> None:
        if data is None:
            data = self.read_sram()
        self._sdk.switch_diag_save_csv(data, filename)

    def save_registers(
        self,
        cfg: SwitchDiagnosticianConfig,
        filename: str,
    ) -> None:
        self._sdk.switch_diag_save_registers(cfg, filename)

    def get_last_error(self) -> str:
        return self._sdk.switch_diag_get_last_error()

    def set_log_level(self, level: int) -> None:
        self._sdk.switch_diag_set_log_level(level)

    def log_enable(self, enable: bool) -> None:
        self._sdk.switch_diag_log_enable(1 if enable else 0)

    def get_signal_table(self, mode: int) -> Dict[str, _SignalDescriptor]:
        return self._sdk.switch_diag_list_signals(mode)

    def read_register(self, offset: int) -> int:
        return self._sdk.switch_diag_reg_read(self._ensure_handle(), offset)

    def write_register(self, offset: int, value: int) -> None:
        self._sdk.switch_diag_reg_write(self._ensure_handle(), offset, value)
class RetimerSDKDrive:
    """Retimer SDK Drive封装类"""

    @staticmethod
    def _encode_path_arg(path: str) -> bytes:
        fs_path = os.fspath(path)
        if isinstance(fs_path, str):
            return fs_path.encode("utf-8")
        return fs_path

    def _raise_switch_diag_error(self, action: str, ret: Optional[int] = None) -> None:
        detail = self.switch_diag_get_last_error()
        if detail:
            raise RuntimeError(f"{action}: {detail}")
        if ret is not None:
            raise RuntimeError(f"{action} (code {ret})")
        raise RuntimeError(action)

    def _check_switch_diag_ret(self, ret: int, action: str) -> None:
        if ret != 0:
            self._raise_switch_diag_error(action, ret)

    def __init__(self, dll_path: Optional[str] = None):
        """初始化SDK Drive库"""
        if dll_path is None:
            dll_path = self._find_dll()

        if not os.path.exists(dll_path):
            raise FileNotFoundError(f"Cannot find retimer_sdk_drive.dll at {dll_path}")

        dll_path = os.path.abspath(dll_path)
        dll_dir = os.path.dirname(dll_path)
        if hasattr(os, "add_dll_directory"):
            os.add_dll_directory(dll_dir)
        else:
            os.environ["PATH"] = dll_dir + os.pathsep + os.environ.get("PATH", "")

        if sys.platform == "win32":
            usb2iic_dll = _find_usb2iic_dll(dll_dir)
            if usb2iic_dll:
                try:
                    cdll.LoadLibrary(usb2iic_dll)
                except Exception as exc:
                    print(f"Warning: Failed to pre-load USB2UARTSPIIICDLL.dll: {exc}")

        try:
            if sys.platform == "win32":
                from ctypes import WinDLL

                self.lib = WinDLL(dll_path)
            else:
                self.lib = cdll.LoadLibrary(dll_path)
        except OSError as exc:
            error_msg = [
                f"Failed to load {dll_path}",
                f"Error: {exc}",
                "Make sure all dependencies are in the same directory:",
                "  - libretimer_sdk_drive.dll",
                "  - USB2UARTSPIIICDLL.dll",
                "  - MinGW runtime DLLs (if not statically linked)",
            ]
            raise RuntimeError("\n".join(error_msg)) from exc

        self._setup_functions()

    # ------------------------------------------------------------------
    # DLL 定位与函数声明
    # ------------------------------------------------------------------
    def _find_dll(self) -> str:
        """查找DLL文件"""
        search_paths: Iterable[str] = [
            ".",
            "..",
            os.path.join("..", ".."),
        ]
        dll_names = ("libretimer_sdk_drive.dll", "retimer_sdk_drive.dll")

        for base in search_paths:
            for name in dll_names:
                candidate = os.path.join(base, name)
                if os.path.exists(candidate):
                    return candidate

        return dll_names[0]

    def _setup_functions(self) -> None:
        """设置函数原型"""
        # 枚举设备
        self.lib.retimer_enumerate_devices.argtypes = [
            ctypes.c_int,
            ctypes.POINTER(DeviceInfo),
            ctypes.c_int,
        ]
        self.lib.retimer_enumerate_devices.restype = ctypes.c_int

        # 设备管理
        self.lib.retimer_dev_open.argtypes = [
            ctypes.c_int,
            ctypes.c_int,
            ctypes.c_uint8,
            ctypes.c_int,
            ctypes.c_int,
            ctypes.c_int,
        ]
        self.lib.retimer_dev_open.restype = ctypes.c_void_p

        self.lib.retimer_dev_close.argtypes = [ctypes.c_void_p]
        self.lib.retimer_dev_close.restype = None

        self.lib.retimer_dev_is_open.argtypes = [ctypes.c_void_p]
        self.lib.retimer_dev_is_open.restype = ctypes.c_int

        self.lib.retimer_dev_set_address.argtypes = [
            ctypes.c_void_p,
            ctypes.c_uint8,
        ]
        self.lib.retimer_dev_set_address.restype = ctypes.c_int

        # 寄存器读写
        self.lib.retimer_read_reg32.argtypes = [
            ctypes.c_void_p,
            ctypes.c_uint32,
            ctypes.POINTER(ctypes.c_uint32),
        ]
        self.lib.retimer_read_reg32.restype = ctypes.c_int

        self.lib.retimer_write_reg32.argtypes = [
            ctypes.c_void_p,
            ctypes.c_uint32,
            ctypes.c_uint32,
        ]
        self.lib.retimer_write_reg32.restype = ctypes.c_int

        # 设备信息
        self.lib.retimer_get_device_id.argtypes = [
            ctypes.c_void_p,
            ctypes.POINTER(ctypes.c_int),
            ctypes.POINTER(ctypes.c_int),
            ctypes.POINTER(ctypes.c_int),
        ]
        self.lib.retimer_get_device_id.restype = ctypes.c_int

        self.lib.retimer_dev_get_fw_version.argtypes = [
            ctypes.c_void_p,
            ctypes.POINTER(ctypes.c_int),
            ctypes.POINTER(ctypes.c_int),
            ctypes.POINTER(ctypes.c_int),
        ]
        self.lib.retimer_dev_get_fw_version.restype = ctypes.c_int

        # PVT传感器
        self.lib.retimer_get_pvt_sensors.argtypes = [
            ctypes.c_void_p,
            ctypes.POINTER(PVTSensors),
        ]
        self.lib.retimer_get_pvt_sensors.restype = ctypes.c_int

        # Link状态
        self.lib.retimer_dev_get_link_status.argtypes = [
            ctypes.c_void_p,
            ctypes.POINTER(LinkStatus),
        ]
        self.lib.retimer_dev_get_link_status.restype = ctypes.c_int

        self.lib.retimer_is_link_up.argtypes = [
            ctypes.c_void_p,
            ctypes.c_int,
            ctypes.c_int,
            ctypes.POINTER(ctypes.c_int),
        ]
        self.lib.retimer_is_link_up.restype = ctypes.c_int

        # 眼图
        self.lib.retimer_dev_get_eye_data.argtypes = [
            ctypes.c_void_p,
            ctypes.c_int,
            ctypes.c_int,
            ctypes.POINTER(EyeResult),
            ctypes.POINTER(ctypes.c_int),
        ]
        self.lib.retimer_dev_get_eye_data.restype = ctypes.c_int

        self.lib.retimer_dev_get_eye_data_with_time.argtypes = [
            ctypes.c_void_p,
            ctypes.c_int,
            ctypes.c_int,
            ctypes.c_double,
            ctypes.POINTER(EyeResult),
            ctypes.POINTER(ctypes.c_int),
        ]
        self.lib.retimer_dev_get_eye_data_with_time.restype = ctypes.c_int

        # Firmware
        self.lib.retimer_firmware_load.argtypes = [
            ctypes.c_void_p,
            ctypes.c_char_p,
            ctypes.POINTER(ctypes.c_int),
        ]
        self.lib.retimer_firmware_load.restype = ctypes.c_int

        self.lib.retimer_firmware_verify.argtypes = [
            ctypes.c_void_p,
            ctypes.c_char_p,
            ctypes.POINTER(ctypes.c_int),
        ]
        self.lib.retimer_firmware_verify.restype = ctypes.c_int

        self.lib.retimer_firmware_dump.argtypes = [
            ctypes.c_void_p,
            ctypes.c_char_p,
            ctypes.POINTER(ctypes.c_int),
        ]
        self.lib.retimer_firmware_dump.restype = ctypes.c_int

        # Bifurcation
        self.lib.retimer_set_bifurcation.argtypes = [ctypes.c_void_p, ctypes.c_int]
        self.lib.retimer_set_bifurcation.restype = ctypes.c_int

        self.lib.retimer_dev_get_bifurcation.argtypes = [
            ctypes.c_void_p,
            ctypes.POINTER(ctypes.c_int),
        ]
        self.lib.retimer_dev_get_bifurcation.restype = ctypes.c_int

        # 错误处理
        self.lib.retimer_get_last_error.argtypes = []
        self.lib.retimer_get_last_error.restype = ctypes.c_char_p

        self.lib.retimer_set_log_level.argtypes = [ctypes.c_int]
        self.lib.retimer_set_log_level.restype = None

        self.lib.retimer_api_log_enable.argtypes = [ctypes.c_int]
        self.lib.retimer_api_log_enable.restype = None

        # Switch diagnostician
        self.lib.switch_diag_open.argtypes = [
            ctypes.c_int,
            ctypes.c_int,
            ctypes.c_uint8,
            ctypes.c_int,
            ctypes.c_int,
            ctypes.c_int,
        ]
        self.lib.switch_diag_open.restype = ctypes.c_void_p

        self.lib.switch_diag_close.argtypes = [ctypes.c_void_p]
        self.lib.switch_diag_close.restype = None

        self.lib.switch_diag_set_address.argtypes = [
            ctypes.c_void_p,
            ctypes.c_uint8,
        ]
        self.lib.switch_diag_set_address.restype = ctypes.c_int

        self.lib.switch_diag_clock_and_reset_check.argtypes = [
            ctypes.c_void_p,
            ctypes.c_int,
        ]
        self.lib.switch_diag_clock_and_reset_check.restype = ctypes.c_int

        self.lib.switch_diag_start.argtypes = [
            ctypes.c_void_p,
            ctypes.POINTER(SwitchDiagnosticianConfig),
        ]
        self.lib.switch_diag_start.restype = ctypes.c_int

        self.lib.switch_diag_stop.argtypes = [ctypes.c_void_p, ctypes.c_int]
        self.lib.switch_diag_stop.restype = ctypes.c_int

        self.lib.switch_diag_is_stop.argtypes = [
            ctypes.c_void_p,
            ctypes.c_int,
            ctypes.POINTER(ctypes.c_int),
        ]
        self.lib.switch_diag_is_stop.restype = ctypes.c_int

        self.lib.switch_diag_sram_is_full.argtypes = [
            ctypes.c_void_p,
            ctypes.c_int,
            ctypes.POINTER(ctypes.c_int),
        ]
        self.lib.switch_diag_sram_is_full.restype = ctypes.c_int

        self.lib.switch_diag_sram_read.argtypes = [
            ctypes.c_void_p,
            ctypes.c_int,
            ctypes.POINTER(SwitchDiagnosticianData),
        ]
        self.lib.switch_diag_sram_read.restype = ctypes.c_int

        self.lib.switch_diag_save_csv.argtypes = [
            ctypes.POINTER(SwitchDiagnosticianData),
            ctypes.c_char_p,
        ]
        self.lib.switch_diag_save_csv.restype = ctypes.c_int

        self.lib.switch_diag_save_registers.argtypes = [
            ctypes.POINTER(SwitchDiagnosticianConfig),
            ctypes.c_char_p,
        ]
        self.lib.switch_diag_save_registers.restype = ctypes.c_int

        self.lib.switch_diag_get_last_error.argtypes = []
        self.lib.switch_diag_get_last_error.restype = ctypes.c_char_p

        self.lib.switch_diag_set_log_level.argtypes = [ctypes.c_int]
        self.lib.switch_diag_set_log_level.restype = None

        self.lib.switch_diag_log_enable.argtypes = [ctypes.c_int]
        self.lib.switch_diag_log_enable.restype = None

        self.lib.switch_diag_list_signals.argtypes = [ctypes.c_int]
        self.lib.switch_diag_list_signals.restype = ctypes.POINTER(_DiaSignalTable)

        self.lib.switch_diag_reg_read.argtypes = [
            ctypes.c_void_p,
            ctypes.c_uint32,
            ctypes.POINTER(ctypes.c_uint32),
        ]
        self.lib.switch_diag_reg_read.restype = ctypes.c_int

        self.lib.switch_diag_reg_write.argtypes = [
            ctypes.c_void_p,
            ctypes.c_uint32,
            ctypes.c_uint32,
        ]
        self.lib.switch_diag_reg_write.restype = ctypes.c_int
    # ------------------------------------------------------------------
    # 公共方法
    # ------------------------------------------------------------------
    def get_last_error(self) -> str:
        error = self.lib.retimer_get_last_error()
        if error:
            return error.decode("utf-8", errors="ignore")
        return ""

    def set_log_level(self, level: int) -> None:
        self.lib.retimer_set_log_level(level)

    def log_enable(self, enable: bool) -> None:
        self.lib.retimer_api_log_enable(1 if enable else 0)

    # ------------------------------------------------------------------
    # Switch Diagnostician API
    # ------------------------------------------------------------------
    def create_switch_diagnostician(
        self,
        adapter_type: int,
        adapter_port: int,
        slave_addr: int,
        *,
        switch_port: int,
        bitrate_khz: int = 400,
        pec_enable: bool = True,
        chip_version: int = 1,
    ) -> SwitchDiagnostician:
        return SwitchDiagnostician(
            self,
            adapter_type,
            adapter_port,
            slave_addr,
            switch_port=switch_port,
            bitrate_khz=bitrate_khz,
            pec_enable=pec_enable,
            chip_version=chip_version,
        )

    def switch_diag_open(
        self,
        adapter_type: int,
        port: int,
        slave_addr: int,
        bitrate_khz: int,
        pec_enable: int,
        chip_version: int,
    ):
        handle = self.lib.switch_diag_open(
            adapter_type,
            port,
            slave_addr,
            bitrate_khz,
            pec_enable,
            chip_version,
        )
        if not handle:
            self._raise_switch_diag_error("Failed to open switch diagnostician")
        return handle

    def switch_diag_close(self, handle) -> None:
        if handle:
            self.lib.switch_diag_close(handle)

    def switch_diag_set_address(self, handle, address: int) -> None:
        ret = self.lib.switch_diag_set_address(handle, address)
        self._check_switch_diag_ret(ret, "Failed to set switch diagnostician address")

    def switch_diag_clock_and_reset_check(self, handle, port: int) -> None:
        ret = self.lib.switch_diag_clock_and_reset_check(handle, port)
        self._check_switch_diag_ret(ret, "Diagnostician clock/reset check failed")

    def switch_diag_start(self, handle, config: SwitchDiagnosticianConfig) -> None:
        ret = self.lib.switch_diag_start(handle, ctypes.byref(config))
        self._check_switch_diag_ret(ret, "Failed to start switch diagnostician")

    def switch_diag_stop(self, handle, port: int) -> None:
        ret = self.lib.switch_diag_stop(handle, port)
        self._check_switch_diag_ret(ret, "Failed to stop switch diagnostician")

    def switch_diag_is_stop(self, handle, port: int) -> bool:
        value = ctypes.c_int(0)
        ret = self.lib.switch_diag_is_stop(handle, port, ctypes.byref(value))
        self._check_switch_diag_ret(ret, "Failed to query diagnostician stop status")
        return bool(value.value)

    def switch_diag_sram_is_full(self, handle, port: int) -> bool:
        value = ctypes.c_int(0)
        ret = self.lib.switch_diag_sram_is_full(handle, port, ctypes.byref(value))
        self._check_switch_diag_ret(ret, "Failed to query diagnostician SRAM status")
        return bool(value.value)

    def switch_diag_sram_read(
        self,
        handle,
        port: int,
        data: SwitchDiagnosticianData,
    ) -> SwitchDiagnosticianData:
        ret = self.lib.switch_diag_sram_read(handle, port, ctypes.byref(data))
        self._check_switch_diag_ret(ret, "Failed to read diagnostician SRAM")
        return data

    def switch_diag_save_csv(
        self,
        data: SwitchDiagnosticianData,
        filename: str,
    ) -> None:
        path = self._encode_path_arg(filename)
        ret = self.lib.switch_diag_save_csv(ctypes.byref(data), path)
        self._check_switch_diag_ret(ret, "Failed to save diagnostician CSV")

    def switch_diag_save_registers(
        self,
        config: SwitchDiagnosticianConfig,
        filename: str,
    ) -> None:
        path = self._encode_path_arg(filename)
        ret = self.lib.switch_diag_save_registers(ctypes.byref(config), path)
        self._check_switch_diag_ret(ret, "Failed to save diagnostician registers")

    def switch_diag_get_last_error(self) -> str:
        error = self.lib.switch_diag_get_last_error()
        if error:
            return error.decode("utf-8", errors="ignore")
        return ""

    def switch_diag_set_log_level(self, level: int) -> None:
        self.lib.switch_diag_set_log_level(level)

    def switch_diag_log_enable(self, enable: int) -> None:
        self.lib.switch_diag_log_enable(enable)

    def switch_diag_list_signals(self, mode: int) -> Dict[str, _SignalDescriptor]:
        table_ptr = self.lib.switch_diag_list_signals(mode)
        if not table_ptr:
            raise RuntimeError(f"Failed to query diagnostician signals for mode {mode}")
        table = table_ptr.contents
        result: Dict[str, _SignalDescriptor] = {}
        for idx in range(table.sig_num):
            signal = table.sig[idx]
            if not signal.signal_name:
                continue
            name = signal.signal_name.decode("utf-8", errors="ignore")
            segments: List[_SignalSegment] = []
            for seg_idx in range(signal.reg_sram_num):
                entry = signal.reg_sram[seg_idx]
                if entry.bits == 0:
                    continue
                segments.append(
                    _SignalSegment(
                        reg_no=int(entry.reg_no),
                        sram_no=int(entry.sram_no),
                        msb=int(entry.msb),
                        lsb=int(entry.lsb),
                        bits=int(entry.bits),
                    )
                )
            result[name] = _SignalDescriptor(int(signal.total_bits), tuple(segments))
        return result

    def switch_diag_reg_read(self, handle, offset: int) -> int:
        value = ctypes.c_uint32()
        ret = self.lib.switch_diag_reg_read(handle, ctypes.c_uint32(offset), ctypes.byref(value))
        self._check_switch_diag_ret(ret, f"Failed to read register 0x{offset:08X}")
        return value.value

    def switch_diag_reg_write(self, handle, offset: int, value: int) -> None:
        ret = self.lib.switch_diag_reg_write(
            handle,
            ctypes.c_uint32(offset),
            ctypes.c_uint32(value),
        )
        self._check_switch_diag_ret(ret, f"Failed to write register 0x{offset:08X}")

    def enumerate_devices(self, adapter_type: int = -1) -> List[dict]:
        devices = (DeviceInfo * 16)()
        count = self.lib.retimer_enumerate_devices(adapter_type, devices, 16)

        if count < 0:
            raise RuntimeError(f"Failed to enumerate devices: {self.get_last_error()}")

        result = []
        for i in range(count):
            result.append(
                {
                    "type": devices[i].type,
                    "port": devices[i].port,
                    "high_speed": devices[i].high_speed,
                    "status": devices[i].status.decode("utf-8", errors="ignore"),
                    "description": devices[i].description.decode(
                        "utf-8", errors="ignore"
                    ),
                }
            )

        return result

    def open_device(
        self,
        adapter_type: int,
        port: int,
        slave_addr: int,
        bitrate_khz: int = 100,
        pec_enable: bool = True,
        chip_version: int = 1,
    ):
        handle = self.lib.retimer_dev_open(
            adapter_type,
            port,
            slave_addr,
            bitrate_khz,
            1 if pec_enable else 0,
            chip_version,
        )

        if not handle:
            raise RuntimeError(f"Failed to open device: {self.get_last_error()}")

        return handle

    def close_device(self, handle) -> None:
        self.lib.retimer_dev_close(handle)

    def read_reg32(self, handle, offset: int) -> int:
        value = ctypes.c_uint32()
        ret = self.lib.retimer_read_reg32(handle, offset, ctypes.byref(value))

        if ret != 0:
            raise RuntimeError(
                f"Failed to read register 0x{offset:08X}: {self.get_last_error()}"
            )

        return value.value

    def write_reg32(self, handle, offset: int, value: int) -> None:
        ret = self.lib.retimer_write_reg32(handle, offset, value)

        if ret != 0:
            raise RuntimeError(
                f"Failed to write register 0x{offset:08X}: {self.get_last_error()}"
            )

    def get_device_id(self, handle):
        vendor = ctypes.c_int()
        device = ctypes.c_int()
        revision = ctypes.c_int()

        ret = self.lib.retimer_get_device_id(
            handle, ctypes.byref(vendor), ctypes.byref(device), ctypes.byref(revision)
        )

        if ret != 0:
            raise RuntimeError(f"Failed to get device ID: {self.get_last_error()}")

        return vendor.value, device.value, revision.value

    def get_fw_version(self, handle):
        major = ctypes.c_int()
        minor = ctypes.c_int()
        build = ctypes.c_int()

        ret = self.lib.retimer_dev_get_fw_version(
            handle, ctypes.byref(major), ctypes.byref(minor), ctypes.byref(build)
        )

        if ret != 0:
            raise RuntimeError(
                f"Failed to get firmware version: {self.get_last_error()}"
            )

        return major.value, minor.value, build.value

    def get_pvt_sensors(self, handle):
        sensors_array = PVTSensors()
        ret = self.lib.retimer_get_pvt_sensors(handle, ctypes.byref(sensors_array))

        if ret != 0:
            raise RuntimeError(f"Failed to get PVT sensors: {self.get_last_error()}")

        result = []
        for i in range(sensors_array.pvt_num):
            pvt = sensors_array.pvt[i]
            result.append(
                {
                    "voltage": pvt.vol,
                    "temperature": pvt.temp,
                    "lvt": pvt.lvt,
                    "ulvt": pvt.ulvt,
                    "svt": pvt.svt,
                    "vol_reg_data": pvt.vol_reg_data,
                    "temp_reg_data": pvt.temp_reg_data,
                    "lvt_reg_data": pvt.lvt_reg_data,
                    "ulvt_reg_data": pvt.ulvt_reg_data,
                    "svt_reg_data": pvt.svt_reg_data,
                }
            )

        return result

    def get_link_status(self, handle):
        status = LinkStatus()
        ret = self.lib.retimer_dev_get_link_status(handle, ctypes.byref(status))

        if ret != 0:
            raise RuntimeError(f"Failed to get link status: {self.get_last_error()}")

        result = {
            "bif": status.bif,
            "link_num": status.link_num,
            "link_is_reset": status.link_is_reset != 0,
            "links": [],
        }

        for i in range(8):
            link = status.link[i]
            result["links"].append(
                {
                    "linkup": link.linkup != 0,
                    "ltssm": link.ltssm,
                    "link_no": link.link_no,
                    "width": link.width,
                    "active_width": link.active_width,
                    "downgrade": link.downgrade != 0,
                    "lane_h": link.lane_h,
                    "lane_l": link.lane_l,
                    "speed": link.speed,
                    "active_lanes": link.active_lanes,
                    "same_link_lanes": link.same_link_lanes,
                    "b_rx_det_lanes": link.b_rx_det_lanes,
                    "a_rx_det_lanes": link.a_rx_det_lanes,
                }
            )

        return result

    def get_eye_data(
        self,
        handle,
        side: int,
        lane: int,
        meas_time: Optional[float] = 0.001,
        progress_callback: Optional[callable] = None,
    ):
        eye_result = EyeResult()
        progress = ctypes.c_int(0)

        if meas_time is not None:
            ret = self.lib.retimer_dev_get_eye_data_with_time(
                handle,
                side,
                lane,
                meas_time,
                ctypes.byref(eye_result),
                ctypes.byref(progress),
            )
        else:
            ret = self.lib.retimer_dev_get_eye_data(
                handle,
                side,
                lane,
                ctypes.byref(eye_result),
                ctypes.byref(progress),
            )

        if ret != 0:
            raise RuntimeError(f"Failed to get eye data: {self.get_last_error()}")

        if progress_callback is not None:
            progress_callback(progress.value)

        return {
            "valid": eye_result.valid != 0,
            "right_ui": eye_result.right_ui,
            "left_ui": eye_result.left_ui,
            "top_mv": eye_result.top_mv,
            "bot_mv": eye_result.bot_mv,
            "width_ui": eye_result.right_ui - eye_result.left_ui,
            "height_mv": eye_result.top_mv - eye_result.bot_mv,
            "progress": progress.value,
        }

    def load_firmware(
        self,
        handle,
        filename: str,
        progress_callback: Optional[callable] = None,
    ) -> bool:
        if not os.path.exists(filename):
            raise FileNotFoundError(f"Firmware file not found: {filename}")

        progress = ctypes.c_int(0)
        filename_bytes = filename.encode("utf-8")

        ret = self.lib.retimer_firmware_load(
            handle, filename_bytes, ctypes.byref(progress)
        )

        if ret != 0:
            raise RuntimeError(f"Failed to load firmware: {self.get_last_error()}")

        if progress_callback is not None:
            progress_callback(progress.value)

        return True

    def verify_firmware(
        self,
        handle,
        filename: str,
        progress_callback: Optional[callable] = None,
    ) -> bool:
        if not os.path.exists(filename):
            raise FileNotFoundError(f"Firmware file not found: {filename}")

        progress = ctypes.c_int(0)
        filename_bytes = filename.encode("utf-8")

        ret = self.lib.retimer_firmware_verify(
            handle, filename_bytes, ctypes.byref(progress)
        )

        if ret != 0:
            raise RuntimeError(
                f"Firmware verification failed: {self.get_last_error()}"
            )

        if progress_callback is not None:
            progress_callback(progress.value)

        return True

    def dump_firmware(
        self,
        handle,
        filename: str,
        progress_callback: Optional[callable] = None,
    ) -> bool:
        progress = ctypes.c_int(0)
        filename_bytes = filename.encode("utf-8")

        ret = self.lib.retimer_firmware_dump(
            handle, filename_bytes, ctypes.byref(progress)
        )

        if ret != 0:
            raise RuntimeError(f"Failed to dump firmware: {self.get_last_error()}")

        if progress_callback is not None:
            progress_callback(progress.value)

        return True


def _find_usb2iic_dll(base_dir: str) -> Optional[str]:
    candidates = [
        os.path.join(base_dir, "USB2UARTSPIIICDLL.dll"),
        os.path.join(base_dir, "usb2iic", "USB2UARTSPIIICDLL.dll"),
    ]

    for path in candidates:
        if os.path.exists(path):
            return path
    return None


