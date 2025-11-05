document.addEventListener("DOMContentLoaded", () => {
    const form = document.getElementById("memoryForm");
    const analysisEl = document.getElementById("analysis");
    const imageEl = document.getElementById("memoryImage");
    const spinner = document.getElementById("spinner");
    const retryBtn = document.getElementById("retryBtn");

    let lastInput = {};
    let isSubmitting = false;

    const callMemoryAPI = async (text, date) => {
        spinner.style.display = "inline-block";
        analysisEl.textContent = "";
        imageEl.src = "";
        retryBtn.style.display = "none";

        try {
            const response = await fetch("/memory/create", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ text, date })
            });

            const data = await response.json();

            if (response.ok && data.status === "success") {
                const parsed = data.gpt_analysis;

                analysisEl.innerHTML = `
                    <div class="analysis-box text-start" style="padding-left: 15px;">
                        <p><strong>감정:</strong> ${parsed.emotion || parsed.감정 || "-"}</p>
                        <p><strong>이미지:</strong> ${parsed.imagery || parsed.이미지 || "-"}</p>
                        <p><strong>상징:</strong> ${parsed.symbolism || parsed.상징 || "-"}</p>
                        <p><strong>시대:</strong> ${parsed.time_period || parsed.시대 || "-"}</p>
                    </div>
                `;
                imageEl.src = data.image_url;
                retryBtn.style.display = "inline-block";
            } else {
                analysisEl.textContent = data.message || "복원 실패";
            }
        } catch (err) {
            console.error(err);
            analysisEl.textContent = "서버 요청 중 오류가 발생했습니다.";
        } finally {
            spinner.style.display = "none";
            isSubmitting = false;
        }
    };

    form.addEventListener("submit", async (e) => {
        e.preventDefault();

        if (isSubmitting) return;
        isSubmitting = true;

        const text = document.getElementById("memoryText").value.trim();
        const date = document.getElementById("memoryDate").value.trim();

        if (!text) {
            alert("기억 내용을 입력해주세요!");
            isSubmitting = false;
            return;
        }

        lastInput = { text, date };
        await callMemoryAPI(text, date);
    });

    retryBtn.addEventListener("click", () => {
        if (lastInput.text && !isSubmitting) {
            isSubmitting = true;
            callMemoryAPI(lastInput.text, lastInput.date);
        }
    });

    // --- Navbar scroll effect ---
    const navbar = document.getElementById("mainNavbar");
    window.addEventListener("scroll", () => {
        if (window.scrollY > 50) {
            document.body.classList.add("scrolled");
        } else {
            document.body.classList.remove("scrolled");
        }
    });
});
