document.addEventListener("DOMContentLoaded", async () => {
    const container = document.getElementById("timelineContainer");
    const modalImage = document.getElementById("modalImage");
    const modalMemory = document.getElementById("modalMemory");
    const modalAnalysis = document.getElementById("modalAnalysis");
    const modalDate = document.getElementById("modalDate");
    const memoryModal = new bootstrap.Modal(document.getElementById("memoryModal"));
    const editModal = new bootstrap.Modal(document.getElementById("editMemoryModal"));

    const editBtn = document.getElementById("editBtn");
    const deleteBtn = document.getElementById("deleteBtn");
    const saveEditBtn = document.getElementById("saveEditBtn");
    const editText = document.getElementById("editText");
    const editDate = document.getElementById("editDate");

    let memories = [];
    let currentMemoryId = null;
    let currentCard = null;

    const safelyParseJSON = (text) => {
        try {
            return JSON.parse(text);
        } catch (err) {
            console.warn("gpt_analysis JSON parse failed:", err);
            return null;
        }
    };

    const renderAnalysis = (analysis) => {
        const parsed = typeof analysis === "string" ? safelyParseJSON(analysis) : analysis;
        if (!parsed) return "<p>AI 분석 데이터가 없습니다.</p>";
        return `
            <div class="analysis-box text-start">
                <p><strong>감정:</strong> ${parsed.emotion || parsed["감정"] || "-"}</p>
                <p><strong>이미지:</strong> ${parsed.imagery || parsed["이미지"] || "-"}</p>
                <p><strong>상징:</strong> ${parsed.symbolism || parsed["상징"] || "-"}</p>
                <p><strong>시대:</strong> ${parsed.time_period || parsed["시대"] || "-"}</p>
            </div>
        `;
    };

    const renderCard = (memory) => {
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
            modalAnalysis.innerHTML = renderAnalysis(memory.gpt_analysis);
            memoryModal.show();
        });

        col.appendChild(card);
        container.appendChild(col);
    };

    const loadMemories = async () => {
        container.innerHTML = "";
        const response = await fetch("/memory/all");
        memories = await response.json();

        if (!memories.length) {
            container.innerHTML = "<p class='text-light'>저장된 기억이 없습니다.</p>";
            return;
        }

        memories.forEach(renderCard);
    };

    editBtn.addEventListener("click", () => {
        if (!currentMemoryId) return alert("선택된 기억이 없습니다.");
        editText.value = modalMemory.textContent;
        editDate.value = modalDate.textContent;
        memoryModal.hide();
        editModal.show();
    });

    saveEditBtn.addEventListener("click", async () => {
        if (!currentMemoryId) return alert("수정할 기억이 없습니다.");
        const updatedText = editText.value.trim();
        const updatedDate = editDate.value.trim();
        if (!updatedText || !updatedDate) {
            alert("내용과 날짜를 모두 입력해주세요.");
            return;
        }
        if (!confirm("정말 수정하시겠습니까?")) return;

        const targetMemory = memories.find((m) => m.id === currentMemoryId);
        const existingAnalysis = targetMemory?.gpt_analysis || {};

        try {
            const res = await fetch(`/memory/${currentMemoryId}`, {
                method: "PUT",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({
                    text: updatedText,
                    date: updatedDate,
                    gpt_analysis: existingAnalysis,
                }),
            });

            const result = await res.json();
            if (res.ok && result.status === "success") {
                alert("기억 수정 및 이미지 생성이 완료되었습니다.");
                editModal.hide();

                if (currentCard) {
                    if (result.image_url) {
                        currentCard.querySelector(".card-img").src = result.image_url;
                    }
                    currentCard.querySelector(".card-memory").textContent = updatedText;
                    currentCard.querySelector(".card-date").textContent = updatedDate;
                }

                if (targetMemory) {
                    targetMemory.text = updatedText;
                    targetMemory.date = updatedDate;
                    if (result.image_url) targetMemory.image_url = result.image_url;
                }

                // 모달 내용도 최신값으로 갱신
                modalImage.src = result.image_url || modalImage.src;
                modalMemory.textContent = updatedText;
                modalDate.textContent = updatedDate;
                modalAnalysis.innerHTML = renderAnalysis(existingAnalysis);

                memoryModal.hide();
            } else {
                alert("수정 실패: " + (result.message || "오류 발생"));
            }
        } catch (error) {
            console.error("수정 요청 오류:", error);
            alert("서버 오류로 수정에 실패했습니다.");
        }
    });

    deleteBtn.addEventListener("click", async () => {
        if (!currentMemoryId) return alert("삭제할 기억이 없습니다.");
        if (!confirm("정말 이 기억을 삭제하시겠습니까?")) return;

        try {
            const res = await fetch(`/memory/${currentMemoryId}`, { method: "DELETE" });
            const result = await res.json();

            if (res.ok && result.status === "success") {
                alert("기억이 삭제되었습니다.");
                memoryModal.hide();

                if (currentCard) currentCard.remove();
                memories = memories.filter((m) => m.id !== currentMemoryId);
            } else {
                alert("삭제 실패: " + (result.message || "오류 발생"));
            }
        } catch (error) {
            console.error("삭제 요청 오류:", error);
            alert("서버 오류로 삭제에 실패했습니다.");
        }
    });

    try {
        await loadMemories();
    } catch (err) {
        console.error(err);
        container.innerHTML = "<p class='text-danger'>데이터 로드 중 오류가 발생했습니다.</p>";
    }
});
