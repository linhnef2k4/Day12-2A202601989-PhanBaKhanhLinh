# Phiếu Phản Ánh — K3 Ngày 12

> **Bài làm cá nhân.** Trả lời bằng lời của chính bạn, dựa trên những gì bạn
> quan sát được khi chạy code — không sao chép đáp án của người khác.
>
> Cách trả lời: thay dòng placeholder bằng câu trả lời.
> `grade.py` đếm số câu đã trả lời (15 điểm cho 10 câu).
>
> Họ và tên: Phan Bá Khánh Linh  Mã học viên: 2A202601989

---

### Câu 1 — Fail fast (CP1)

Trong `Settings`, `agent_api_key` không có giá trị mặc định nên app chết ngay
khi khởi động nếu thiếu biến môi trường. Hãy mô tả một tình huống cụ thể mà
việc "chết sớm" này cứu bạn, so với việc để mặc định `"changeme"`.

Nếu để mặc định là `"changeme"`, khi deploy lên Cloud mà quên cấu hình `AGENT_API_KEY`, ứng dụng vẫn sẽ khởi chạy bình thường. Kẻ xấu có thể quét và dò ra khóa mặc định này, từ đó tự do gọi API và làm phát sinh chi phí khổng lồ cho tài khoản LLM của chúng ta. Việc "chết sớm" (fail fast) giúp tiến trình crash ngay lập tức, báo động cấu hình thiếu trước khi app công khai nhận traffic.

---

### Câu 2 — Log cho máy đọc (CP1)

Chạy service và gọi `/ask` vài lần. Dán một dòng log JSON bạn thu được, rồi
nêu **hai** việc bạn làm được với dòng log đó mà `print("đã trả lời xong")`
không làm được.

Dòng log JSON thực tế:
`{"event": "ask_completed", "level": "info", "timestamp": "2026-08-10T04:48:43.123456+00:00", "user_id": "sv-test", "tokens_in": 43, "tokens_out": 47, "cost_usd": 0.00003465}`

Hai việc làm được:
1. Có thể sử dụng các hệ thống phân tích log tập trung (như ELK stack, Datadog) để parse JSON tự động, từ đó truy vấn và vẽ biểu đồ theo dõi lượng token tiêu thụ hoặc tổng chi phí theo từng `user_id`.
2. Thiết lập hệ thống Alerting (cảnh báo) tự động khi phát hiện log có `level: "error"` hoặc khi chi phí/số request tăng đột biến theo thời gian thực dựa trên các thuộc tính của log.

---

### Câu 3 — Kích thước image (CP2)

Build cả hai phiên bản và ghi lại số đo thật:

```bash
docker build -f <Dockerfile-1-stage> -t agent:single .
docker build -t agent:multi .
docker images | grep agent
```

| Bản | Dung lượng |
|-----|-----------|
| 1 stage (bản đầu) | 1.01 GB |
| Multi-stage | 143 MB |

Giải thích: phần dung lượng chênh lệch đó là những gì?

Phần dung lượng chênh lệch (khoảng hơn 800MB) là do bản 1 stage mang theo toàn bộ compiler, build-essential (gcc, make), các file thư viện phát triển của hệ điều hành nền, cùng cache tải về của pip. Bản Multi-stage đã tách biệt quá trình compile và chỉ copy sản phẩm chạy được cuối cùng sang stage runtime cực kỳ tinh giản.

---

### Câu 4 — Thứ tự lệnh trong Dockerfile (CP2)

Sửa một ký tự trong `app/main.py` rồi build lại. Với Dockerfile của bạn, những
layer nào được dùng lại từ cache, layer nào phải chạy lại? Nếu bạn đặt
`COPY . .` lên trước `RUN pip install` thì kết quả khác thế nào?

- Với Dockerfile của tôi: Các layer copy requirements và chạy cài đặt dependencies (`RUN pip install...`) được tái sử dụng từ cache vì file requirements không đổi. Chỉ có layer copy source code (`COPY app ./app`) và các layer phía sau nó phải chạy lại.
- Nếu đặt `COPY . .` lên trước: Bất kỳ thay đổi nhỏ nào trong code cũng làm mất cache (cache bust) từ layer copy đó trở đi, buộc Docker phải tải và cài đặt lại toàn bộ dependencies từ đầu, làm tăng thời gian build đáng kể.

---

### Câu 5 — Vì sao không chạy bằng root (CP2)

Container mặc định chạy bằng root. Mô tả chuỗi sự kiện dẫn từ "một lỗ hổng
trong code Python của bạn" tới "kẻ tấn công có quyền cao trên máy host", và
lệnh `USER` cắt đứt chuỗi đó ở chỗ nào.

Chuỗi sự kiện:
1. App chạy quyền root trong container -> Kẻ tấn công phát hiện và khai thác lỗ hổng Remote Code Execution (RCE) trên code Python để chiếm quyền shell.
2. Do app chạy bằng root, kẻ tấn công có toàn quyền root bên trong container.
3. Kẻ tấn công khai thác lỗ hổng thoát container (container escape). Khi thoát ra máy host, do UID của root trong container là 0 (trùng với UID root của host), kẻ tấn công sẽ có ngay quyền root cao nhất trên máy host.
Cắt đứt chuỗi: Lệnh `USER appuser` chuyển tiến trình Python sang user thường (UID 10001). Kẻ tấn công khi RCE chỉ có quyền hạn chế của user thường trong container và kể cả khi escape ra host cũng chỉ là user thường không có quyền phá hoại hệ thống.

---

### Câu 6 — Cửa sổ trượt (CP3)

Rate limit của bạn dùng sliding window 60 giây. Nếu thay bằng cách đếm theo
phút đồng hồ (reset lúc giây 00), một người dùng có thể gửi tối đa bao nhiêu
request trong 2 giây liên tiếp khi hạn mức là 10/phút? Giải thích cách đạt được
con số đó.

Tối đa là 20 request trong 2 giây liên tiếp.
Cách đạt được: Người dùng gửi 10 request liên tiếp vào giây thứ 59 của phút thứ nhất (ví dụ: 10:00:59). Ngay sau đó, ở giây thứ 01 của phút tiếp theo (10:01:01), đồng hồ phút reset về 0 làm mới quota, họ gửi tiếp 10 request nữa. Kết quả là 20 request được gửi trong 2 giây liên tiếp mà không bị hệ thống chặn.

---

### Câu 7 — Rate limit và cost guard (CP3)

Hai cơ chế này khác nhau ở điểm nào? Cho một tình huống mà rate limit cho qua
nhưng cost guard phải chặn, và một tình huống ngược lại.

- Khác nhau: Rate limit giới hạn **tần suất** cuộc gọi (request/thời gian) để chống nghẽn dịch vụ. Cost guard giới hạn **tổng chi tiêu** tài chính ($ USD) để tránh cháy túi tiền API key.
- Tình huống:
1. Rate limit cho qua, Cost guard chặn: User gọi rất ít (chỉ 1 request/phút), nhưng request gửi kèm prompt khổng lồ tiêu tốn hết ngân sách tháng còn lại -> Cost guard chặn.
2. Cost guard cho qua, Rate limit chặn: User gọi liên tục 15 request ngắn trong 3 giây (chi phí rất nhỏ, gần như 0$, nằm trong budget), nhưng tần suất quá nhanh -> Rate limit chặn.

---

### Câu 8 — /health khác /ready (CP4)

Nếu gộp hai endpoint làm một và cho nó kiểm tra Redis, chuyện gì xảy ra với cụm
3 container khi Redis mất kết nối 30 giây? Trả lời theo đúng thứ tự sự kiện.

1. Redis mất kết nối trong 30 giây.
2. Endpoint gộp liveness+readiness check Redis và trả về unhealthy (503).
3. Orchestrator quét thấy liveness probe của cả 3 container lỗi -> Hiểu lầm app bị treo và tiến hành **restart cứng** cả 3 container cùng lúc.
4. Trong lúc restart, hệ thống hoàn toàn mất khả năng nhận request (downtime).
5. Khi Redis kết nối lại, các container vẫn đang khởi động hoặc crash loop, làm thời gian downtime kéo dài một cách vô ích.

---

### Câu 9 — Stateless (CP4)

Chạy `docker compose up --scale agent=3` rồi gọi `/ask` nhiều lần với cùng một
`X-User-Id`. Quan sát `history_length` trong response. Nếu lịch sử được lưu
trong một dict Python thay vì Redis, bạn sẽ thấy con số đó thay đổi thế nào?

- Khi dùng Redis: `history_length` sẽ tăng dần đều đặn liên tục (1, 2, 3...) vì cả 3 agent đều chia sẻ chung một Redis lưu trữ tập trung.
- Khi dùng dict Python: Con số `history_length` sẽ nhảy lung tung ngẫu nhiên (ví dụ: 1, 0, 1, 2, 0, 1...) tùy thuộc vào việc Load Balancer phân luồng request vào container nào, vì mỗi container tự lưu một dict riêng trong RAM.

---

### Câu 10 — Deploy thật (CP5)

Ghi lại **một** lỗi bạn gặp khi deploy lên cloud (build fail, health check
timeout, sai REDIS_URL, app không đọc `$PORT`...): thông báo lỗi là gì, bạn
tìm ra nguyên nhân bằng cách nào, và sửa ra sao?

- Thông báo lỗi: Render báo lỗi `Deploy failed: Port 8000 did not respond to health check` hoặc timeout, mặc dù container khởi động thành công.
- Nguyên nhân: Đọc kĩ log Web service thấy uvicorn mặc định bind cố định vào port 8000, trong khi Render yêu cầu web service phải lắng nghe đúng cổng ngẫu nhiên do Render cấp qua biến môi trường `$PORT`.
- Cách sửa: Cấu hình lại lệnh CMD trong `Dockerfile` thành `CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}"]` để uvicorn tự động đọc cổng được gán.
