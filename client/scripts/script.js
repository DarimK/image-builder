const img = document.getElementById("img");
const apiURL = (window.location.hostname === "www.darim.me") ? "https://imagebuilder.onrender.com" : "http://localhost:5000";


async function apiImageFetch(endpoint, formData) {
    try {
        const response = await fetch(`${apiURL}/${endpoint}`, {
            method: "POST",
            body: formData
        });
        if (response.headers.get("content-type") === "image/png") {
            const blob = await response.blob();
            img.src = URL.createObjectURL(blob);
        } else {
            const data = await response.json();
            alert(`Error: ${data.error}`);
        }
    } catch(e) {
        console.error("Error:", error);
        alert("An error occurred. Please try again.");
    }
}