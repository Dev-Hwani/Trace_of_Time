document.addEventListener("DOMContentLoaded", async () => {
    const container = document.getElementById("timelineContainer");
    const modalImage = document.getElementById("modalImage");
    const modalMemory = document.getElementById("modalMemory");
    const modalAnalysis = document.getElementById("modalAnalysis");
    const modalDate = document.getElementById("modalDate");
    const memoryModalEl = document.getElementById('memoryModal');
    const memoryModal = new bootstrap.Modal(memoryModalEl);
    const editModal = new bootstrap.Modal(document.getElementById('editMemoryModal'));

    const editBtn = document.getElementById("editBtn");
    const deleteBtn = document.getElementById("deleteBtn");
    const saveEditBtn = document.getElementById("saveEditBtn");
    const editText = document.getElementById("editText");
    const editDate = document.getElementById("editDate");

    let currentMemoryId = null;
    let currentCard = null;

    try {
        const response = await fetch("/memory/all");
        const memories = await response.json();

        if (!memories.length) {
            container.innerHTML = "<p class='text-light'>저장된 기억이 없습니다.</p>";
            return;
        }

        memories.forEach(memory => {
            let analysisHTML = "";
            try {
                const parsed = typeof memory.gpt_analysis === "string"
                    ? JSON.parse(memory.gpt_analysis)
                    : memory.gpt_analysis;

                analysisHTML = `
                    <div class="analysis-box text-start">
                        <p><strong>감정:</strong> ${parsed.emotion || parsed.감정 || "-"}</p>
                        <p><strong>이미지:</strong> ${parsed.imagery || parsed.이미지 || "-"}</p>
                        <p><strong>상징:</strong> ${parsed.symbolism || parsed.상징 || "-"}</p>
                        <p><strong>시대:</strong> ${parsed.time_period || parsed.시대 || "-"}</p>
                    </div>
                `;
            } catch (error) {
                console.warn("gpt_analysis 파싱 실패:", error);
                analysisHTML = `<p>AI 분석 데이터를 불러올 수 없습니다.</p>`;
            }

            const col = document.createElement("div");
            col.className = "col-lg-4 col-md-6";

            const card = document.createElement("div");
            card.className = "timeline-card p-3 rounded shadow bg-dark text-light";
            card.style.cursor = "pointer";
            card.dataset.id = memory.id;

            card.innerHTML = `
                <img src="${memory.image_url}" class="img-fluid rounded mb-2 card-img" alt="${memory.text.substring(0, 30)}">
                <h5 class="card-date">${memory.date}</h5>
                <p class="card-memory text-truncate">${memory.text}</p>
                <button class="btn btn-outline-light mt-2 w-100 btn-view-detail">상세 보기</button>
            `;

            card.querySelector(".btn-view-detail").addEventListener("click", () => {
                currentMemoryId = memory.id;
                currentCard = card;

                modalImage.src = memory.image_url;
                modalMemory.textContent = memory.text;
                modalDate.textContent = memory.date;
                modalAnalysis.innerHTML = analysisHTML;

                memoryModal.show();
            });

            col.appendChild(card);
            container.appendChild(col);
        });

        // 수정 버튼 클릭
        editBtn.addEventListener("click", () => {
            if (!currentMemoryId) return alert("선택된 기억이 없습니다.");
            editText.value = modalMemory.textContent;
            editDate.value = modalDate.textContent;
            memoryModal.hide();
            editModal.show();
        });

        // 수정 저장
        saveEditBtn.addEventListener("click", async () => {
            if (!currentMemoryId) return alert("수정할 기억이 없습니다.");
            const updatedText = editText.value.trim();
            const updatedDate = editDate.value.trim();
            if (!updatedText || !updatedDate) {
                alert("내용과 날짜를 모두 입력해주세요.");
                return;
            }
            if (!confirm("정말로 수정하시겠습니까?")) return;

            try {
                const res = await fetch(`/memory/${currentMemoryId}`, {
                    method: "PUT",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({
                        text: updatedText,
                        date: updatedDate,
                        gpt_analysis: {}
                    }),
                });

                const result = await res.json();
                if (res.ok && result.status === "success") {
                    alert("✅ 수정 및 이미지 재생성이 완료되었습니다!");
                    editModal.hide();

                    if (result.image_url && currentCard) {
                        currentCard.querySelector(".card-img").src = result.image_url;
                    }
                    if (currentCard) {
                        currentCard.querySelector(".card-memory").textContent = updatedText;
                        currentCard.querySelector(".card-date").textContent = updatedDate;
                    }
                    memoryModal.hide();
                } else {
                    alert("❌ 수정 실패: " + (result.message || "오류 발생"));
                }
            } catch (error) {
                console.error("수정 요청 실패:", error);
                alert("❌ 서버 오류로 수정에 실패했습니다.");
            }
        });

        // 삭제
        deleteBtn.addEventListener("click", async () => {
            if (!currentMemoryId) return alert("삭제할 기억이 없습니다.");
            if (!confirm("정말 이 기억을 삭제하시겠습니까?")) return;

            try {
                const res = await fetch(`/memory/${currentMemoryId}`, { method: "DELETE" });
                const result = await res.json();

                if (res.ok && result.status === "success") {
                    alert("🗑 삭제가 완료되었습니다!");
                    memoryModal.hide();
                    currentCard.remove();
                } else {
                    alert("❌ 삭제 실패: " + (result.message || "오류 발생"));
                }
            } catch (error) {
                console.error("삭제 요청 실패:", error);
                alert("❌ 서버 오류로 삭제에 실패했습니다.");
            }
        });

    } catch (err) {
        console.error(err);
        container.innerHTML = "<p class='text-danger'>타임라인 로드 중 오류가 발생했습니다.</p>";
    }
});
