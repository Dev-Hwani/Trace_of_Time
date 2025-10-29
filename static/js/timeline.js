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
            // gpt_analysis 처리
            let analysisHTML = "";
            try {
                const parsed = typeof memory.gpt_analysis === "string"
                    ? JSON.parse(memory.gpt_analysis)
                    : memory.gpt_analysis;

                // JSON 구조를 사람이 보기 좋게 HTML 포맷으로 정리
                analysisHTML = `
                    <div class="analysis-box text-start">
                        <p><strong>감정:</strong> ${parsed.emotion || "-"}</p>
                        <p><strong>이미지:</strong> ${parsed.imagery || "-"}</p>
                        <p><strong>상징:</strong> ${parsed.symbolism || "-"}</p>
                        <p><strong>시대:</strong> ${parsed.time_period || "-"}</p>
                    </div>
                `;
            } catch (error) {
                console.warn("gpt_analysis 파싱 실패:", error);
                analysisHTML = `<p>AI 분석 데이터를 불러올 수 없습니다.</p>`;
            }

            // 카드 구성
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

            // 상세 보기 버튼 클릭 시 모달 표시
            card.querySelector(".btn-view-detail").addEventListener("click", () => {
                modalImage.src = memory.image_url;
                modalMemory.textContent = memory.text;
                modalDate.textContent = memory.date;

                // 모달 내용은 HTML로 표시되도록 (가독성 개선)
                modalAnalysis.innerHTML = analysisHTML;

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
