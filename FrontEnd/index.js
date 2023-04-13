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

const createCard = (data) => {
    console.log(data);
    parentCard = document.createElement("div");
    parentCard.classList.add("card");

    cardBody = document.createElement("div");
    cardBody.classList.add("card-body");
    parentCard.appendChild(cardBody);

    cardTitle = document.createElement("h3");
    cardTitle.classList.add("card-title");
    cardTitle.appendChild(document.createTextNode("File: " + data["filename"].split(".")[0]));
    cardBody.appendChild(cardTitle);

    cardText = document.createElement("p");
    cardText.classList.add("card-text");
    cardText.appendChild(
        document.createTextNode(
            "Total Time            : " + data["totalTime"]));
    cardBody.appendChild(cardText);

    cardText = document.createElement("p");
    cardText.classList.add("card-text");
    cardText.appendChild(
        document.createTextNode(
            "Concurrent Cycle Time : " + data["totalTimeConcurrentCycle"]));
    cardBody.appendChild(cardText);

    cardText = document.createElement("p");
    cardText.classList.add("card-text");
    cardText.appendChild(
        document.createTextNode(
            "Pause Young Time      : " + data["totalTimePauseYoung"]));
    cardBody.appendChild(cardText);

    cardText = document.createElement("p");
    cardText.classList.add("card-text");
    cardText.appendChild(
        document.createTextNode(
            "Average Cycle Time    : " + data["avgTime"]));
    cardBody.appendChild(cardText);

    cardText = document.createElement("p");
    cardText.classList.add("card-text");
    cardText.appendChild(
        document.createTextNode(
            "Minimum Cycle Time    : " + data["minPauseTime"]));
    cardBody.appendChild(cardText);

    cardText = document.createElement("p");
    cardText.classList.add("card-text");
    cardText.appendChild(
        document.createTextNode(
            "Maximum Cycle Time    : " + data["maxPauseTime"]));
    cardBody.appendChild(cardText);
    
    cardImage = document.createElement("img");
    cardImage.classList.add("card-img");
    cardImage.setAttribute("src", data["stackBarChart"]);
    parentCard.appendChild(cardImage);

    cardImage = document.createElement("img");
    cardImage.classList.add("card-img");
    cardImage.setAttribute("src", data["timeline"]);
    parentCard.appendChild(cardImage);

    document.body.appendChild(parentCard);
};


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
        .then(async (response) => {
            if (!response.ok) {
                throw new Error(response.statusText);
            }
            return await response.json();
        })
        .then((data) => {
            createCard(data);
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
        .then(async (response) => {
            if (!response.ok) {
                throw new Error(response.statusText);
            }
            return await response.json();
        })
        .then((data) => {
            createCard(data);
        })
        .catch((error) => {
            console.error("Error uploading file:", error);
        });
});
