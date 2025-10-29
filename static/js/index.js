document.addEventListener("DOMContentLoaded", () => {
    const form = document.getElementById("memoryForm");
    const analysisEl = document.getElementById("analysis");
    const imageEl = document.getElementById("memoryImage");
    const spinner = document.getElementById("spinner");
    const retryBtn = document.getElementById("retryBtn");

    let lastInput = {};

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

            if (data.gpt_analysis && data.image_url) {
                analysisEl.textContent = data.gpt_analysis.analysis;
                imageEl.src = data.image_url;
                retryBtn.style.display = "inline-block";
            } else {
                analysisEl.textContent = "복원 실패";
            }
        } catch (err) {
            console.error(err);
            analysisEl.textContent = "서버 요청 중 오류가 발생했습니다.";
        } finally {
            spinner.style.display = "none";
        }
    };

    form.addEventListener("submit", (e) => {
        e.preventDefault();
        const text = document.getElementById("memoryText").value;
        const date = document.getElementById("memoryDate").value;

        if (!text) {
            alert("기억 내용을 입력해주세요!");
            return;
        }

        lastInput = { text, date };
        callMemoryAPI(text, date);
    });

    retryBtn.addEventListener("click", () => {
        if (lastInput.text) {
            callMemoryAPI(lastInput.text, lastInput.date);
        }
    });
});

// Navbar scroll effect
document.addEventListener("DOMContentLoaded", () => {
    const navbar = document.getElementById("mainNavbar");
    window.addEventListener("scroll", () => {
        if (window.scrollY > 50) {
            document.body.classList.add("scrolled");
        } else {
            document.body.classList.remove("scrolled");
        }
    });
});
