#!/usr/bin/env python3
"""Kiểm tra chất lượng CSV công việc (task_id, owner, hours) và in JSON ra stdout.

Cách chạy (cwd là workspace):
    python skills/csv-quality/scripts/check_csv.py --input data/tasks.csv

Exit 0: phân tích thành công, kể cả khi dữ liệu có lỗi chất lượng.
Exit 1: file không tồn tại/không đọc được, thiếu cột bắt buộc hoặc lỗi parse CSV; thông báo ra stderr.
Script chỉ đọc, không sửa CSV và không tính tổng giờ/KPI.
"""



from __future__ import annotations

import argparse
import csv
import json
import math
import sys

REQUIRED_COLUMNS = ("task_id", "owner", "hours")
REASON_ORDER = (
    "wrong_field_count",
    "missing_task_id",
    "duplicate_id",
    "missing_owner",
    "invalid_hours",
)


class InputError(Exception):
    pass


def parse_hours(raw: str | None) -> float | None:
    """Số giờ hợp lệ: số hữu hạn, không âm. Trả None nếu không hợp lệ."""
    if raw is None or not raw.strip():
        return None
    try:
        value = float(raw.strip())
    except ValueError:
        return None
    if not math.isfinite(value) or value < 0:
        return None
    return value


def parse_max_hours(raw: str) -> float:
    try:
        value = float(raw.strip())
    except ValueError as exc:
        raise argparse.ArgumentTypeError(
            "--max-hours phải là số hữu hạn không âm."
        ) from exc

    if not math.isfinite(value) or value < 0:
        raise argparse.ArgumentTypeError(
            "--max-hours phải là số hữu hạn không âm."
        )
    return value


def analyze(path: str, max_hours: float) -> dict:
    try:
        handle = open(path, encoding="utf-8-sig", newline="")
    except OSError as exc:
        raise InputError(
            f"Không đọc được file {path}: {exc.strerror or exc}"
        ) from exc

    with handle:
        reader = csv.reader(handle, strict=True)

        try:
            header = next(reader, None)
            if header is None:
                raise InputError(f"File {path} rỗng, không có header.")

            columns = [c.strip() for c in header]
            missing = [c for c in REQUIRED_COLUMNS if c not in columns]
            if missing:
                raise InputError(
                    f"Thiếu cột bắt buộc: {', '.join(missing)}. "
                    f"Header hiện có: {', '.join(columns)}"
                )

            index = {name: columns.index(name) for name in REQUIRED_COLUMNS}

            row_count = 0
            missing_owner = 0
            invalid_hours = 0
            first_seen: dict[str, int] = {}
            duplicate_ids: list[str] = []
            issues: list[dict] = []

            hours_by_owner: dict[str, float] = {}
            excluded_rows: list[dict] = []

            for row in reader:
                line = reader.line_num

                if not any(cell.strip() for cell in row):
                    continue

                row_count += 1

                def cell(name: str) -> str:
                    position = index[name]
                    return row[position].strip() if position < len(row) else ""

                task_id = cell("task_id")
                owner = cell("owner")
                hours = cell("hours")

                reasons: list[str] = []

                if len(row) != len(columns):
                    reasons.append("wrong_field_count")
                    issues.append({
                        "line": line,
                        "column": None,
                        "type": "wrong_field_count",
                        "task_id": task_id or None,
                        "message": (
                            f"Có {len(row)} trường, "
                            f"header có {len(columns)} cột."
                        ),
                    })

                if not task_id:
                    reasons.append("missing_task_id")
                    issues.append({
                        "line": line,
                        "column": "task_id",
                        "type": "missing_task_id",
                        "task_id": None,
                        "message": "task_id trống.",
                    })
                elif task_id in first_seen:
                    reasons.append("duplicate_id")

                    if task_id not in duplicate_ids:
                        duplicate_ids.append(task_id)

                    issues.append({
                        "line": line,
                        "column": "task_id",
                        "type": "duplicate_id",
                        "task_id": task_id,
                        "message": (
                            f"task_id {task_id} đã xuất hiện "
                            f"ở line {first_seen[task_id]}."
                        ),
                    })
                else:
                    # Quan trọng: giữ lần xuất hiện đầu tiên dù dữ liệu
                    # của dòng đó sau này có invalid.
                    first_seen[task_id] = line

                if not owner:
                    missing_owner += 1
                    reasons.append("missing_owner")
                    issues.append({
                        "line": line,
                        "column": "owner",
                        "type": "missing_owner",
                        "task_id": task_id or None,
                        "message": "owner trống.",
                    })

                parsed_hours = parse_hours(hours)
                if parsed_hours is None:
                    invalid_hours += 1
                    reasons.append("invalid_hours")
                    issues.append({
                        "line": line,
                        "column": "hours",
                        "type": "invalid_hours",
                        "task_id": task_id or None,
                        "value": hours,
                        "message": (
                            f"hours '{hours}' không phải "
                            "số hữu hạn không âm."
                        ),
                    })

                if reasons:
                    excluded_rows.append({
                        "line": line,
                        "task_id": task_id or None,
                        "reasons": [
                            reason for reason in REASON_ORDER if reason in reasons
                        ],
                    })
                    continue

                hours_by_owner[owner] = (
                    hours_by_owner.get(owner, 0) + parsed_hours
                )

        except csv.Error as exc:
            raise InputError(
                f"Lỗi parse CSV ở line {reader.line_num}: {exc}"
            ) from exc
        except UnicodeDecodeError as exc:
            raise InputError(
                f"File {path} không phải UTF-8: {exc}"
            ) from exc

    overloaded_owners = [
        {
            "owner": owner,
            "total_hours": total,
        }
        for owner, total in sorted(hours_by_owner.items())
        if total > max_hours
    ]

    return {
        "input": path,
        "row_count": row_count,
        "missing_owner_count": missing_owner,
        "invalid_hours_count": invalid_hours,
        "duplicate_id_count": len(duplicate_ids),
        "duplicate_ids": duplicate_ids,
        "issues": sorted(issues, key=lambda item: item["line"]),
        "max_hours": max_hours,
        "hours_by_owner": hours_by_owner,
        "overloaded_owners": overloaded_owners,
        "excluded_rows": sorted(excluded_rows, key=lambda item: item["line"]),
    }


def main(argv: list[str] | None = None) -> int:
    if sys.stdout:
        sys.stdout.reconfigure(encoding="utf-8")
    if sys.stderr:
        sys.stderr.reconfigure(encoding="utf-8")

    parser = argparse.ArgumentParser(
        description="Kiểm tra chất lượng CSV và tính tổng giờ theo owner."
    )
    parser.add_argument(
        "--input",
        required=True,
        help="Đường dẫn CSV, ví dụ data/tasks.csv",
    )
    parser.add_argument(
        "--max-hours",
        required=True,
        type=parse_max_hours,
        help="Ngưỡng giờ tối đa để xác định người quá tải.",
    )

    args = parser.parse_args(argv)

    try:
        result = analyze(args.input, args.max_hours)
    except InputError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1

    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())