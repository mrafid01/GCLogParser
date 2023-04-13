const dragDrop = document.querySelector(".drag-drop");
const fileInput = document.querySelector("#file-input");

dragDrop.addEventListener("dragover", (e) => {
    e.preventDefault();
    dragDrop.classList.add("drag-over");
});

dragDrop.addEventListener("dragleave", (e) => {
    e.preventDefault();
    dragDrop.classList.remove("drag-over");
});

dragDrop.addEventListener("drop", (e) => {
    e.preventDefault();
    dragDrop.classList.remove("drag-over");
    const file = e.dataTransfer.files[0];
    if (file.name.split(".").pop() != "log") {
        alert("Invalid file type, please upload a .log file");
        return;
    }
    const formData = new FormData();
    formData.append("file", file);
    fetch("http://localhost:5000/upload", {
        method: "POST",
        body: formData,
    })
        .then((response) => {
            if (!response.ok) {
                throw new Error(response.statusText);
            }
            return response.json();
        })
        .then((data) => {
            console.log(data);
            console.log("File uploaded successfully:", data);
        })
        .catch((error) => {
            console.error("Error uploading file:", error);
        });
});

fileInput.addEventListener("change", () => {
    const file = fileInput.files[0];
    if (file.name.split(".").pop() != "log") {
        alert("Invalid file type, please upload a .log file");
        return;
    }
    const formData = new FormData();
    formData.append("file", file);
    fetch("http://localhost:5000/upload", {
        method: "POST",
        body: formData,
    })
        .then((response) => {
            if (!response.ok) {
                throw new Error(response.statusText);
            }
            return response.json();
        })
        .then((data) => {
            console.log(data);
            console.log("File uploaded successfully:", data);
        })
        .catch((error) => {
            console.error("Error uploading file:", error);
        });
});
