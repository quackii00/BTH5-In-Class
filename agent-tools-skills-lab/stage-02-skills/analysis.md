# Analysis

## 1. Kiểm tra tool `list_files`

| Trường hợp | Input | Kết quả |
|---|---|---|
| Thư mục hợp lệ | `data/policies/` | PASS — liệt kê được các policy documents |
| Truyền file thay vì thư mục | `data/policies/refund-policy-current.md` | PASS — trả về `NOT_A_DIRECTORY` |
| Path không tồn tại | `data/policies/not-found` | PASS — trả về `DIRECTORY_NOT_FOUND` |
| Path thoát workspace | `../` | PASS — trả về `PATH_OUTSIDE_WORKSPACE` |

### Kết quả

Tool `list_files` chỉ cho phép truy cập trong workspace, không đệ quy vào thư mục con và xử lý đúng các trường hợp path không hợp lệ.

Khi kiểm tra `data/policies/`, tool tìm thấy:

- `data/policies/refund-policy-current.md`
- `data/policies/refund-policy-legacy.md`

## 2. Case A

### Input

- Purchase date: `28/09/2026`
- Refund request date: `06/10/2026`
- Activation status: `Not activated`

### Kết quả

- **Chính sách áp dụng:** Refund Policy — Legacy
- **Số ngày đã qua:** 8 ngày
- **Kết luận:** Không đủ điều kiện
- **Phí:** Không áp dụng
- **Tài liệu căn cứ:** `data/policies/refund-policy-legacy.md`

Policy Legacy áp dụng cho các giao dịch trước `01/10/2026` và cho phép hoàn tiền trong vòng 7 ngày. Request được gửi sau 8 ngày nên không đủ điều kiện.

### Bằng chứng trong trace

- **Model call #1:** `read_file` đọc `skills/refund-policy/SKILL.md`.
- **Model call #2:** `list_files` liệt kê các file trong `data/policies/`.
- **Model call #3:** `read_file` đọc `data/policies/refund-policy-current.md`.
- **Model call #4:** `read_file` đọc `data/policies/refund-policy-legacy.md`.
- **Model call #5:** `read_file` đọc `skills/refund-policy/references/answer-template.md`.
- **Model call #6:** Agent trả lời cuối cùng, không gọi thêm tool.

### Trace summary

- Model calls: `6`
- Tool calls: `5`
- Tools provided: `3`
- Skills in catalog: `2`
- Skill content loaded into history: `1`
- Resources read: `3`
- Output files: `0`

### Kết luận

**Case A: PASS**

Agent sử dụng `list_files` để tìm các policy documents trong `data/policies/`, sau đó sử dụng `read_file` để đọc policy và chọn chính sách dựa trên purchase date.

---

## 3. Case B

> Sẽ cập nhật sau khi chạy Case B.

---

## 4. Missing information

> Sẽ cập nhật sau khi kiểm tra trường hợp thiếu activation status.

---

## 5. Rename policy files

> Sẽ cập nhật sau khi đổi tên hai policy files và chạy lại Case A/B để kiểm tra agent không phụ thuộc vào tên file cố định.
## 3. Case B

### Input

* Purchase date: `02/10/2026`
* Refund request date: `12/10/2026`
* Activation status: `Not activated`

### Kết quả

* **Chính sách áp dụng:** Refund Policy — Current
* **Số ngày đã qua:** 10 ngày
* **Kết luận:** Đủ điều kiện hoàn tiền
* **Phí:** Không có phí
* **Tài liệu căn cứ:** `data/policies/refund-policy-current.md`

Policy Current áp dụng cho các giao dịch từ `01/10/2026` trở đi và cho phép hoàn tiền trong vòng 14 ngày nếu sản phẩm chưa được kích hoạt. Request được gửi sau 10 ngày nên đủ điều kiện.

### Bằng chứng trong trace

* **Model call #1:** `read_file` đọc `skills/refund-policy/SKILL.md`.
* **Model call #2:** `list_files` liệt kê các file trong `data/policies/`.
* **Model call #3:** `read_file` đọc `data/policies/refund-policy-current.md`.
* **Model call #4:** `read_file` đọc `skills/refund-policy/references/answer-template.md`.
* **Model call #5:** Agent trả lời cuối cùng, không gọi thêm tool.

### Trace summary

* Model calls: `5`
* Tool calls: `4`
* Tools provided: `3`
* Skills in catalog: `2`
* Skill content loaded into history: `1`
* Resources read: `2`
* Output files: `0`
* Conversation: `b2bf6b9a`

### Kết luận

**Case B: PASS**


## 4. Missing information

### Input

* Purchase date: `02/10/2026`
* Refund request date: `12/10/2026`
* Activation status: **Không được cung cấp**

### Kết quả

Agent **không đưa ra kết luận hoàn tiền** và hỏi lại người dùng về trạng thái kích hoạt:

> Bạn có thể cho biết sản phẩm đã được kích hoạt chưa? (Cần biết trạng thái kích hoạt để xác định quyền hoàn tiền.)

Điều này đúng với yêu cầu của skill: khi thiếu activation status, agent phải hỏi người dùng và **không được giả định sản phẩm chưa được kích hoạt**.

### Bằng chứng trong trace

* **Model call #1:** `read_file` đọc `skills/refund-policy/SKILL.md`.
* Skill xác định `activation status` là thông tin bắt buộc.
* **Model call #2:** Agent hỏi lại trạng thái kích hoạt và không gọi thêm tool.

### Trace summary

* Model calls: `2`
* Tool calls: `1`
* Tools provided: `3`
* Skills in catalog: `2`
* Skill content loaded into history: `1`
* Resources read: `0`
* Output files: `0`
* Conversation: `26bf0344`

### Kết luận

**Missing information: PASS**

Agent xử lý đúng trường hợp thiếu thông tin bằng cách hỏi lại activation status thay vì tự giả định trạng thái của sản phẩm.

## 5. Rename policy files

### Thay đổi

Hai policy documents được đổi tên:

* `data/policies/refund-policy-current.md`
  → `data/policies/current-refund-rules.md`
* `data/policies/refund-policy-legacy.md`
  → `data/policies/legacy-refund-rules.md`

Nội dung của các policy không thay đổi.

### Rename Test — Case A

#### Input

* Purchase date: `28/09/2026`
* Refund request date: `06/10/2026`
* Activation status: `Not activated`

#### Kết quả

* **Chính sách áp dụng:** Refund Policy — Legacy
* **Số ngày đã qua:** 8 ngày
* **Kết luận:** Không đủ điều kiện
* **Phí:** Không có phí
* **Tài liệu căn cứ:** `data/policies/legacy-refund-rules.md`

Policy Legacy áp dụng cho các giao dịch trước `01/10/2026` và chỉ cho phép hoàn tiền trong vòng 7 ngày. Request được gửi sau 8 ngày nên không đủ điều kiện.

#### Bằng chứng trong trace

* **Model call #1:** `list_files` tìm các policy documents và phát hiện tên file mới.
* **Model call #2:** `read_file` đọc `skills/refund-policy/SKILL.md`.
* **Model call #3:** `read_file` đọc `data/policies/current-refund-rules.md`.
* **Model call #4:** `read_file` đọc `data/policies/legacy-refund-rules.md`.
* **Model call #5:** `read_file` đọc `skills/refund-policy/references/answer-template.md`.
* **Model call #6:** Agent trả lời cuối cùng.

#### Trace summary

* Model calls: `6`
* Tool calls: `5`
* Tools provided: `3`
* Skills in catalog: `2`
* Skill content loaded into history: `1`
* Resources read: `3`
* Output files: `0`
* Conversation: `35459b56`

### Kết luận

**Rename Test — Case A: PASS**

Sau khi đổi tên policy files, agent vẫn tìm và sử dụng đúng tài liệu bằng cách gọi `list_files` để khám phá nội dung của `data/policies/`. Agent không phụ thuộc vào tên file cũ và đưa ra kết luận giống Case A ban đầu.
### Rename Test — Case B

#### Input

* Purchase date: `02/10/2026`
* Refund request date: `12/10/2026`
* Activation status: `Not activated`

#### Kết quả

* **Chính sách áp dụng:** Refund Policy — Current
* **Số ngày đã qua:** 10 ngày
* **Kết luận:** Đủ điều kiện hoàn tiền
* **Phí:** Không có phí
* **Tài liệu căn cứ:** `data/policies/current-refund-rules.md`

Policy Current áp dụng cho các giao dịch từ `01/10/2026` trở đi và cho phép hoàn tiền trong vòng 14 ngày nếu sản phẩm chưa được kích hoạt. Request được gửi sau 10 ngày nên đủ điều kiện.

#### Bằng chứng trong trace

* **Model call #1:** `read_file` đọc `skills/refund-policy/SKILL.md`.
* **Model call #2:** `list_files` tìm các policy documents với tên file mới.
* **Model call #3:** `read_file` đọc `data/policies/current-refund-rules.md`.
* **Model call #4:** `read_file` đọc `skills/refund-policy/references/answer-template.md`.
* **Model call #5:** Agent trả lời cuối cùng.

#### Trace summary

* Model calls: `5`
* Tool calls: `4`
* Tools provided: `3`
* Skills in catalog: `2`
* Skill content loaded into history: `1`
* Resources read: `2`
* Output files: `0`
* Conversation: `089ee8d3`

### Kết luận

**Rename Test — Case B: PASS**

Sau khi đổi tên policy files, agent vẫn tự khám phá `data/policies/` bằng `list_files` và sử dụng đúng policy mới. Kết luận không thay đổi so với Case B trước khi rename.

Cả hai rename tests đều cho thấy agent **không phụ thuộc vào tên file cố định**.
