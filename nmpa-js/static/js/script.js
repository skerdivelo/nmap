document.getElementById("scan-button").addEventListener("click", async () => {
    const startIP = document.getElementById("start-ip").value;
    const endIP = document.getElementById("end-ip").value;
    const port = document.getElementById("port").value;
    const endpoint = document.getElementById("endpoint").value;
    const doLogin = document.getElementById("login-toggle").checked;

    if (!startIP || !endIP || !port) {
        alert("Please fill in all required fields.");
        return;
    }

    const output = document.getElementById("output");
    output.innerHTML = "<p>Scanning...</p>";

    try {
        const response = await fetch("/scan", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ startIP, endIP, port, endpoint }),
        });

        if (!response.ok) throw new Error("Server error");

        const results = await response.json();

        if (results.length === 0) {
            output.innerHTML = "<p>No available endpoints found.</p>";
            return;
        }

        if (!doLogin) {
            // If login is not selected, only display available endpoints
            output.innerHTML = "<p>Available Endpoints:</p>";
            results.forEach((url) => {
                output.innerHTML += `<p><a href="${url}" target="_blank">${url}</a></p>`;
            });
            return;
        }

        // Login process
        output.innerHTML = "<p>Logging into servers...</p>";

        // Show password modal
        const passwordModal = document.getElementById("password-modal");
        passwordModal.classList.remove("hidden");

        document
            .getElementById("password-submit")
            .addEventListener("click", async () => {
                const password =
                    document.getElementById("password-input").value;
                if (!password) {
                    alert("Password is required to proceed.");
                    return;
                }

                passwordModal.classList.add("hidden");

                for (const url of results) {
                    const loginResponse = await fetch("/login", {
                        method: "POST",
                        headers: { "Content-Type": "application/json" },
                        body: JSON.stringify({
                            urls: [url],
                            password: password,
                        }),
                    });

                    let loginResult;
                    try {
                        loginResult = await loginResponse.json();
                    } catch (error) {
                        throw new Error("Invalid JSON response from server");
                    }

                    if (loginResult[0].status === "success") {
                        output.innerHTML += `<p>Logged in to <a href="${url}" target="_blank">${url}</a>: Server Name - ${loginResult[0].serverName}</p>`;
                    } else {
                        output.innerHTML += `<p>Failed to log in to <a href="${url}" target="_blank">${url}</a>: ${loginResult[0].reason}</p>`;
                    }
                }
            });
    } catch (error) {
        output.innerHTML = `<p>Error: ${error.message}</p>`;
    }
});
