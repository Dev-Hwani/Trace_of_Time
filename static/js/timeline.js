document.addEventListener("DOMContentLoaded", async () => {
    const container = document.getElementById("timelineContainer");
    const modalImage = document.getElementById("modalImage");
    const modalMemory = document.getElementById("modalMemory");
    const modalAnalysis = document.getElementById("modalAnalysis");
    const modalDate = document.getElementById("modalDate");
    const memoryModal = new bootstrap.Modal(document.getElementById('memoryModal'));

    try {
        const response = await fetch("/memory/all");
        const memories = await response.json();

        if (!memories.length) {
            container.innerHTML = "<p class='text-light'>저장된 기억이 없습니다.</p>";
            return;
        }

        memories.forEach(memory => {
            // gpt_analysis가 JSON 문자열이면 파싱
            let analysisText = "";
            try {
                const parsed = typeof memory.gpt_analysis === "string"
                    ? JSON.parse(memory.gpt_analysis)
                    : memory.gpt_analysis;

                analysisText = `
감정: ${parsed.emotion || ""}
이미지: ${parsed.imagery || ""}
상징: ${parsed.symbolism || ""}
시대: ${parsed.time_period || ""}
                `.trim();
            } catch {
                analysisText = memory.gpt_analysis?.analysis || "";
            }

            const col = document.createElement("div");
            col.className = "col-lg-4 col-md-6";

            const card = document.createElement("div");
            card.className = "timeline-card p-3 rounded shadow bg-dark text-light";
            card.style.cursor = "pointer";

            card.innerHTML = `
                <img src="${memory.image_url}" class="img-fluid rounded mb-2 card-img" alt="${memory.text.substring(0, 30)}">
                <h5 class="card-date">${memory.date}</h5>
                <p class="card-memory text-truncate">${memory.text}</p>
                <button class="btn btn-outline-light mt-2 w-100 btn-view-detail">상세 보기</button>
            `;

            card.querySelector(".btn-view-detail").addEventListener("click", () => {
                modalImage.src = memory.image_url;
                modalMemory.textContent = memory.text;
                modalAnalysis.textContent = analysisText;
                modalDate.textContent = memory.date;
                memoryModal.show();
            });

            col.appendChild(card);
            container.appendChild(col);
        });
    } catch (err) {
        console.error(err);
        container.innerHTML = "<p class='text-danger'>타임라인 로드 중 오류가 발생했습니다.</p>";
    }
});
