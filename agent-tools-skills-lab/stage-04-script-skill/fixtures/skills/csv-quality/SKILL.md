# CSV Quality

Kiểm tra chất lượng CSV công việc và tính tổng giờ theo owner.

## Khi sử dụng
Dùng skill khi cần kiểm tra chất lượng file CSV công việc và tính tải theo owner.

## Quy tắc
- Không sửa file CSV đầu vào.
- `task_id`, `owner`, `hours` được strip whitespace.
- Chỉ dòng có đúng số field, `task_id`/`owner` không rỗng và `hours` là số hữu hạn không âm mới được tính tổng.
- Với `task_id` trùng, chỉ occurrence đầu tiên được giữ; các occurrence sau bị loại.
- Owner quá tải khi tổng giờ `>` ngưỡng.
- Nếu người dùng chưa cung cấp ngưỡng, phải hỏi trước khi kết luận.
- Khi cần chạy script Python, phải dùng tool `bash` và đặt lệnh `python ...` bên trong `command`.
- Không có Python tool riêng.

## Chạy script
Trong workspace:

`python skills/csv-quality/scripts/check_csv.py --input data/workload.csv --max-hours <ngưỡng>`

`--max-hours` là bắt buộc và phải là số hữu hạn không âm.

## Báo cáo
Nêu:
1. Ngưỡng `max_hours`.
2. Tổng giờ theo owner (`hours_by_owner`).
3. Owner quá tải (`overloaded_owners`).
4. Các dòng bị loại (`excluded_rows`) và lý do.

Không tự đặt ngưỡng nếu người dùng chưa cung cấp.