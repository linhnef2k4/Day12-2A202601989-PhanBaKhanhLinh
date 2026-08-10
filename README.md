# K3 — Ngày 12: Hạ Tầng Cloud & Deployment (9h00–13h00)

Đưa một AI agent từ `localhost:8000` lên một địa chỉ công khai mà người khác
gọi được, có bảo mật, có giới hạn chi phí, và không sập khi bạn deploy bản mới.

---

## ⚠️ Bài Làm Cá Nhân

**Đây là bài tập cá nhân. Mỗi học viên nộp một repository của riêng mình.**

| Được phép | Không được phép |
|-----------|-----------------|
| Đọc tài liệu, Stack Overflow, tra AI để hiểu khái niệm | Sao chép code của học viên khác |
| Hỏi Lab Coach khi bị kẹt | Dùng chung repo, chung commit history |
| Thảo luận **cách tiếp cận** với bạn cùng lớp | Nhờ người khác làm hộ, kể cả một phần |
| Dùng AI để giải thích lỗi | Nộp code mà bạn không giải thích được |

**Cách kiểm tra:** Lab Coach sẽ chọn ngẫu nhiên học viên để hỏi
trực tiếp về code trong bài nộp. Không giải thích được phần mình viết → điểm
phần đó bị hủy.

**Phát hiện hai bài trùng nhau bất thường (cùng lỗi chính tả, cùng comment,
cùng cấu trúc lạ): cả hai bài đều 0 điểm**, không phân biệt ai chép của ai.

---

## 📦 Cách Đặt Tên Repository

Repo nộp bài **bắt buộc** đặt tên theo mẫu:

```
DAY12-<Mã học viên>-<Họ và Tên>
```

**Quy tắc viết:**
- Họ tên **viết liền, không dấu**, chữ cái đầu mỗi từ viết hoa
- Ngăn cách ba phần bằng dấu gạch ngang `-`
- Không khoảng trắng (GitHub tự đổi khoảng trắng thành `-`, dễ sai lệch)

**Ví dụ:**

| Học viên | Tên repo |
|----------|----------|
| 2A202600280 — Nguyễn Văn An | `DAY12-2A202600280-NguyenVanAn` |
| 2A202601111 — Trần Thị Bích Hà | `DAY12-2A202601111-TranThiBichHa` |

**Sai tên repo = trừ 5 điểm.** Đây là cách duy nhất để Lab Coach biết bài của ai
trong khoảng 1000 repo.

### Tạo repo và bắt đầu làm

```bash
# 1. Fork repo lab về và đổi tên theo cú pháp bên trên
# 2. Clone repo lab về máy
git clone <URL repo bạn đã fork>
cd DAY12-V202400123-NguyenVanAn

# 3. Commit và Push khi hoàn thiện bài lab
git add .
git commit -m "Checkpoint 0"
git push origin main
```

> Commit sau mỗi checkpoint. Lịch sử commit cho thấy bạn tự làm — một commit
> duy nhất vào phút chót là dấu hiệu đáng ngờ.

---

## Mục Tiêu

Sau buổi lab này, bạn sẽ:
- Tách toàn bộ cấu hình ra khỏi code theo 12-Factor và biết vì sao secret không được có giá trị mặc định
- Viết Dockerfile multi-stage, chạy container bằng user thường, image dưới 500MB
- Bảo vệ API bằng API key, sliding-window rate limit và cost guard theo tháng
- Phân biệt liveness/readiness probe, xử lý SIGTERM để deploy không rớt request
- Thiết kế service stateless để scale ngang được
- Deploy lên cloud và có một địa chỉ công khai hoạt động thật

---

## Lịch Trình & Checkpoint

| Giờ | Nội dung | Checkpoint | Điểm |
|-----|----------|------------|------|
| 9h00–9h20 | Setup môi trường, tạo repo đúng tên | **CP0:** `pytest tests/ -v` chạy được (rớt hết là đúng — bạn chưa code) | — |
| 9h20–10h00 | **Block 1** — 12-Factor Config, Health, Logging | **CP1 (10h00):** `pytest tests/test_cp1.py -v` | 15 |
| 10h00–10h45 | **Block 2** — Docker: multi-stage, bảo mật image | **CP2 (10h45):** `pytest tests/test_cp2.py -v` | 15 |
| 10h45–10h55 | ☕ Giải lao | — | — |
| 10h55–11h40 | **Block 3** — API Security: auth, rate limit, cost guard | **CP3 (11h40):** `pytest tests/test_cp3.py -v` | 20 |
| 11h40–12h20 | **Block 4** — Scaling & Reliability | **CP4 (12h20):** `pytest tests/test_cp4.py -v` | 20 |
| 12h20–12h50 | **Block 5** — Deploy lên cloud | **CP5 (12h50):** `pytest tests/test_cp5.py -v` | 15 |
| 12h50–13h00 | Hoàn thiện `exercises.md`, `python grade.py`, nộp bài | | 15 |
| — | **BONUS** — CI/CD với GitHub Actions (không bắt buộc) | `pytest tests/test_bonus_cicd.py -v` | +10 |

**Cách dùng checkpoint:** đến mốc giờ nào thì chạy lệnh của checkpoint đó. Xanh
hết → sang block sau. Còn đỏ → đọc thông báo lỗi (mỗi test đều ghi rõ sai ở đâu
và vì sao điều đó quan trọng), sửa, chạy lại. Kẹt quá 10 phút thì gọi Lab Coach
và **đi tiếp block sau** — làm được đến đâu có điểm đến đó, đừng để tắc một chỗ
mà mất cả các block còn lại.

**Phần BONUS** dành cho bạn nào xong sớm hoặc muốn làm thêm sau buổi lab: tự
viết một workflow GitHub Actions để mỗi lần push là tự chạy test, tự build
image, và chỉ deploy khi mọi thứ xanh. Lab **không cho sẵn file mẫu** — đây là
phần để bạn tự đọc tài liệu và tự dựng. Chỉ nên bắt đầu khi CP1–CP5 đã ổn.

Chi tiết từng bước: [LAB_GUIDE.md](LAB_GUIDE.md).

---

## Cài Đặt

### Yêu cầu
- Python 3.11+
- Docker & Docker Compose (cần cho CP2 trở đi)
- Git + tài khoản GitHub
- Tài khoản Railway hoặc Render (miễn phí, đăng ký ~5 phút — cần cho CP5)

Không cần API key của OpenAI hoặc các bên cung cấp API khác: lab dùng **mock LLM** chạy offline.

### Môi trường ảo & thư viện

**macOS / Linux:**
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

**Windows (PowerShell):**
```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

### File cấu hình

```bash
cp .env.example .env          # Windows: copy .env.example .env
```

Mở `.env`, đổi `AGENT_API_KEY` thành khóa của riêng bạn:

```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

`.env` đã nằm trong `.gitignore` — **không bao giờ commit file này**.

### Redis

```bash
docker compose up -d redis            # cách chuẩn
```

Chưa cài được Docker? Đặt tạm `REDIS_URL=fake://` trong `.env` để dùng Redis giả
trong RAM (đủ để làm CP1/CP3/CP4, nhưng CP2 và CP5 vẫn cần Docker).

---

## Cấu Trúc Thư Mục

```
DAY12-<MãHV>-<HọTên>/
├── README.md              # File này — quy định, lịch trình, chấm điểm, nộp bài
├── LAB_GUIDE.md           # Hướng dẫn chi tiết từng block
├── exercises.md           # 10 câu phản ánh
├── DEPLOYMENT.md          # Điền URL sau khi deploy (CP5 đọc file này)
├── grade.py               # Chấm điểm tự động
├── app/                   # ★ NƠI BẠN VIẾT CODE
│   ├── config.py          #   CP1 — Settings 12-factor
│   ├── logging_utils.py   #   CP1 — log JSON
│   ├── main.py            #   CP1/CP3/CP4 — FastAPI app
│   ├── auth.py            #   CP3 — xác thực API key
│   ├── rate_limiter.py    #   CP3 — sliding window
│   ├── cost_guard.py      #   CP3 — ngân sách theo tháng
│   ├── store.py           #   CP4 — lịch sử hội thoại trong Redis
│   └── lifecycle.py       #   CP4 — graceful shutdown
├── utils/mock_llm.py      # Cho sẵn — LLM giả, không cần API key
├── Dockerfile             # ★ CP2 — sửa thành multi-stage
├── docker-compose.yml     # ★ CP2 — thêm service agent
├── .dockerignore          # ★ CP2 — bổ sung mục còn thiếu
├── nginx/nginx.conf       # Cho sẵn — load balancer (điểm cộng)
├── railway.toml           # CP5 — cấu hình Railway
├── render.yaml            # CP5 — cấu hình Render
├── screenshots/           # Ảnh chụp màn hình bản deploy
├── .github/workflows/     # ★ BONUS — workflow CI/CD bạn tự viết (chưa có sẵn)
└── tests/
    ├── test_cp1.py … test_cp5.py
    ├── test_bonus_cicd.py # BONUS — chấm workflow CI/CD
    └── conftest.py
```

Dấu ★ = file bạn phải sửa (hoặc tự tạo). Các file khác đọc để hiểu, không cần sửa.

---

## Chạy Kiểm Thử

```bash
pytest tests/test_cp1.py -v     # từng checkpoint
pytest tests/ -v                # toàn bộ
pytest tests/ -v -m "not docker"  # bỏ qua test build Docker (chậm)
```

Test dùng Redis giả (`fakeredis`) nên **không cần Redis thật**. Các test build
image tự bỏ qua nếu máy bạn chưa bật Docker.

---

## Chấm Điểm Tự Động (100 điểm)

```bash
python grade.py
```

| Tiêu chí | Cách chấm | Điểm |
|----------|-----------|------|
| CP1 — 12-Factor Config, Health & Logging | `tests/test_cp1.py` | 15 |
| CP2 — Docker: multi-stage, bảo mật image | `tests/test_cp2.py` | 15 |
| CP3 — API Security: auth, rate limit, cost guard | `tests/test_cp3.py` | 20 |
| CP4 — Scaling & Reliability | `tests/test_cp4.py` | 20 |
| CP5 — Cloud Deployment | `tests/test_cp5.py` | 15 |
| `exercises.md` — 10 câu phản ánh | Đếm số câu đã trả lời | 15 |
| **Tổng phần bắt buộc** | | **100** |
| BONUS — CI/CD với GitHub Actions | `tests/test_bonus_cicd.py` | +10 |

Điểm bonus cộng vào tổng nhưng **tổng cuối không vượt quá 100**. Muốn chấm nhanh
phần bắt buộc thôi: `python grade.py --no-bonus`.

Điểm mỗi checkpoint tỷ lệ với số test pass — **làm được đến đâu có điểm đến đó**.

**Trừ điểm:**
- Sai quy tắc đặt tên repo: **−5**
- Commit file `.env` hoặc để lộ API key trong repo: **−10**
- Không giải thích được code khi được hỏi: hủy điểm phần đó

**Không deploy được lên cloud?** Đặt `LOCAL_FALLBACK=true` trong `.env`, chạy
`docker compose up -d`, chụp màn hình vào `screenshots/`. CP5 khi đó tối đa
9/15 điểm. Vẫn hơn là bỏ trắng.

---

## Hướng Dẫn Nộp Bài

```bash
# 1. Kiểm tra lần cuối
python grade.py

# 2. Chắc chắn .env KHÔNG bị commit
git status --porcelain | grep -q "\.env$" && echo "DỪNG LẠI: .env đang bị theo dõi"

# 3. Commit và đẩy lên
git add -A
git commit -m "Hoàn thành lab Day 12"
git push
```

Nộp **link repository** lên Codelab. Repo phải ở chế độ public.

**Hạn nộp:** 23h59 cùng ngày.

---

## Danh Sách Kiểm Tra Trước Khi Nộp

- [ ] Repo đúng tên `DAY12-<MãHV>-<HọTên>`, viết liền không dấu
- [ ] `pytest tests/ -v` — đã chạy và biết rõ test nào còn rớt, vì sao
- [ ] `python grade.py` — xem điểm, mục tiêu ≥ 75/100
- [ ] `exercises.md` — đủ 10 câu, viết bằng lời của mình
- [ ] `DEPLOYMENT.md` — có Public URL thật, không dán giá trị API key
- [ ] `screenshots/` — có ảnh dashboard và ảnh gọi `/health`
- [ ] `.env` **không** nằm trong repo (`git ls-files | grep .env` chỉ ra `.env.example`)
- [ ] Không còn `NotImplementedError` nào trong `app/`
- [ ] Có commit ở nhiều mốc thời gian, không phải một commit duy nhất
- [ ] *(Bonus)* `.github/workflows/ci.yml` chạy xanh, README có badge `passing`
