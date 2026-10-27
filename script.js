/* =========================================================
   DIGITAL LEGACY SYSTEM
   COMMON JAVASCRIPT
   ========================================================= */


/* =========================================================
   1. PASSWORD SHOW / HIDE
   ========================================================= */

function togglePassword(button) {

    const wrapper = button.closest(".password-wrapper");

    if (!wrapper) {
        return;
    }

    const passwordInput = wrapper.querySelector("input");

    if (!passwordInput) {
        return;
    }

    if (passwordInput.type === "password") {

        passwordInput.type = "text";

        button.textContent = "🙈";

        button.setAttribute(
            "aria-label",
            "Hide password"
        );

    } else {

        passwordInput.type = "password";

        button.textContent = "👁️";

        button.setAttribute(
            "aria-label",
            "Show password"
        );
    }
}


/* =========================================================
   2. MOBILE NAVIGATION
   ========================================================= */

function toggleMobileMenu() {

    const navLinks = document.querySelector(".nav-links");

    if (!navLinks) {
        return;
    }

    navLinks.classList.toggle("active");
}


/* =========================================================
   3. CLOSE MOBILE MENU WHEN LINK IS CLICKED
   ========================================================= */

document.addEventListener("DOMContentLoaded", function () {

    const navLinks = document.querySelector(".nav-links");

    if (!navLinks) {
        return;
    }

    const links = navLinks.querySelectorAll("a");

    links.forEach(function (link) {

        link.addEventListener("click", function () {

            navLinks.classList.remove("active");

        });

    });

});


/* =========================================================
   4. PASSWORD VALIDATION
   ========================================================= */

function validatePassword(password) {

    const result = {
        length: password.length >= 8,
        uppercase: /[A-Z]/.test(password),
        lowercase: /[a-z]/.test(password),
        number: /[0-9]/.test(password)
    };

    result.valid =
        result.length &&
        result.uppercase &&
        result.lowercase &&
        result.number;

    return result;
}


/* =========================================================
   5. UPDATE PASSWORD RULES
   ========================================================= */

function updatePasswordRules(passwordInput) {

    if (!passwordInput) {
        return;
    }

    const password = passwordInput.value;

    const rules = validatePassword(password);


    const lengthRule =
        document.getElementById("rule-length");

    const uppercaseRule =
        document.getElementById("rule-uppercase");

    const lowercaseRule =
        document.getElementById("rule-lowercase");

    const numberRule =
        document.getElementById("rule-number");


    if (lengthRule) {

        lengthRule.classList.toggle(
            "rule-valid",
            rules.length
        );

    }


    if (uppercaseRule) {

        uppercaseRule.classList.toggle(
            "rule-valid",
            rules.uppercase
        );

    }


    if (lowercaseRule) {

        lowercaseRule.classList.toggle(
            "rule-valid",
            rules.lowercase
        );

    }


    if (numberRule) {

        numberRule.classList.toggle(
            "rule-valid",
            rules.number
        );

    }
}


/* =========================================================
   6. CONFIRM PASSWORD VALIDATION
   ========================================================= */

function validatePasswordMatch(passwordId, confirmPasswordId) {

    const passwordInput =
        document.getElementById(passwordId);

    const confirmInput =
        document.getElementById(confirmPasswordId);

    if (!passwordInput || !confirmInput) {
        return true;
    }

    return passwordInput.value === confirmInput.value;
}


/* =========================================================
   7. EMAIL VALIDATION
   ========================================================= */

function validateEmail(email) {

    const pattern =
        /^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$/;

    return pattern.test(email);
}


/* =========================================================
   8. INDIAN PHONE VALIDATION
   ========================================================= */

function validateIndianPhone(phone) {

    const pattern =
        /^[6-9][0-9]{9}$/;

    return pattern.test(phone);
}


/* =========================================================
   9. USERNAME VALIDATION
   ========================================================= */

function validateUsername(username) {

    const pattern =
        /^[A-Za-z0-9_]{4,30}$/;

    return pattern.test(username);
}


/* =========================================================
   10. OTP VALIDATION
   ========================================================= */

function validateOTP(otp) {

    const pattern =
        /^[0-9]{6}$/;

    return pattern.test(otp);
}


/* =========================================================
   11. FILE SIZE VALIDATION
   ========================================================= */

function validateFileSize(
    file,
    maxSizeMB = 10
) {

    if (!file) {
        return false;
    }

    const maxBytes =
        maxSizeMB * 1024 * 1024;

    return file.size <= maxBytes;
}


/* =========================================================
   12. FILE EXTENSION VALIDATION
   ========================================================= */

function validateFileExtension(file) {

    if (!file) {
        return false;
    }

    const allowedExtensions = [
        "pdf",
        "png",
        "jpg",
        "jpeg",
        "doc",
        "docx"
    ];

    const filename =
        file.name.toLowerCase();

    const parts =
        filename.split(".");

    if (parts.length < 2) {
        return false;
    }

    const extension =
        parts.pop();

    return allowedExtensions.includes(
        extension
    );
}


/* =========================================================
   13. DOCUMENT UPLOAD VALIDATION
   ========================================================= */

function validateDocumentUpload(fileInput) {

    if (!fileInput || !fileInput.files.length) {
        return false;
    }

    const file =
        fileInput.files[0];

    if (!validateFileExtension(file)) {

        alert(
            "Invalid file type.\n\n" +
            "Allowed formats: PDF, PNG, JPG, JPEG, DOC and DOCX."
        );

        fileInput.value = "";

        return false;
    }


    if (!validateFileSize(file, 10)) {

        alert(
            "File is too large.\n\n" +
            "Maximum allowed size is 10 MB."
        );

        fileInput.value = "";

        return false;
    }

    return true;
}


/* =========================================================
   14. FILE INPUT DISPLAY
   ========================================================= */

function showSelectedFile(input) {

    if (!input || !input.files.length) {
        return;
    }

    const file =
        input.files[0];

    const filenameElement =
        document.getElementById("selected-file-name");

    if (filenameElement) {

        filenameElement.textContent =
            "Selected file: " + file.name;

    }
}


/* =========================================================
   15. DRAG AND DROP UPLOAD
   ========================================================= */

document.addEventListener(
    "DOMContentLoaded",
    function () {

        const uploadBox =
            document.querySelector(".upload-box");

        const fileInput =
            document.querySelector(
                'input[type="file"]'
            );

        if (!uploadBox || !fileInput) {
            return;
        }


        uploadBox.addEventListener(
            "dragover",
            function (event) {

                event.preventDefault();

                uploadBox.classList.add(
                    "drag-over"
                );

            }
        );


        uploadBox.addEventListener(
            "dragleave",
            function () {

                uploadBox.classList.remove(
                    "drag-over"
                );

            }
        );


        uploadBox.addEventListener(
            "drop",
            function (event) {

                event.preventDefault();

                uploadBox.classList.remove(
                    "drag-over"
                );


                const files =
                    event.dataTransfer.files;

                if (!files.length) {
                    return;
                }


                fileInput.files = files;

                showSelectedFile(
                    fileInput
                );

            }
        );

    }
);


/* =========================================================
   16. AUTO-HIDE FLASH MESSAGES
   ========================================================= */

document.addEventListener(
    "DOMContentLoaded",
    function () {

        const alerts =
            document.querySelectorAll(
                ".alert"
            );

        alerts.forEach(function (alert) {

            setTimeout(function () {

                alert.style.opacity = "0";

                alert.style.transition =
                    "opacity 0.4s ease";

                setTimeout(function () {

                    alert.remove();

                }, 400);

            }, 5000);

        });

    }
);


/* =========================================================
   17. DELETE CONFIRMATION
   ========================================================= */

function confirmDelete(itemName) {

    if (!itemName) {
        itemName = "this item";
    }

    return confirm(
        "Are you sure you want to delete " +
        itemName +
        "?\n\nThis action cannot be undone."
    );
}


/* =========================================================
   18. LEGACY DELETE CONFIRMATION
   ========================================================= */

function confirmLegacyDelete() {

    return confirm(
        "Are you sure you want to delete this legacy assignment?\n\n" +
        "This action cannot be undone."
    );
}


/* =========================================================
   19. FORM SUBMIT PROTECTION
   ========================================================= */

document.addEventListener(
    "DOMContentLoaded",
    function () {

        const forms =
            document.querySelectorAll(
                "form"
            );

        forms.forEach(function (form) {

            form.addEventListener(
                "submit",
                function () {

                    const submitButtons =
                        form.querySelectorAll(
                            'button[type="submit"], input[type="submit"]'
                        );

                    submitButtons.forEach(
                        function (button) {

                            if (
                                button.dataset
                                    .noDisable === "true"
                            ) {
                                return;
                            }

                            button.disabled = true;

                            button.style.opacity =
                                "0.7";

                        }
                    );

                }
            );

        });

    }
);


/* =========================================================
   20. PASSWORD LIVE CHECK
   ========================================================= */

document.addEventListener(
    "DOMContentLoaded",
    function () {

        const passwordInputs =
            document.querySelectorAll(
                'input[type="password"]'
            );

        passwordInputs.forEach(
            function (input) {

                input.addEventListener(
                    "input",
                    function () {

                        updatePasswordRules(
                            input
                        );

                    }
                );

            }
        );

    }
);


/* =========================================================
   21. PREVENT DOUBLE CLICK ON BUTTONS
   ========================================================= */

function preventDoubleClick(button) {

    if (!button) {
        return;
    }

    if (button.dataset.clicked === "true") {
        return false;
    }

    button.dataset.clicked = "true";

    setTimeout(function () {

        button.dataset.clicked =
            "false";

    }, 2000);

    return true;
}


/* =========================================================
   22. CURRENT YEAR
   ========================================================= */

document.addEventListener(
    "DOMContentLoaded",
    function () {

        const yearElements =
            document.querySelectorAll(
                ".current-year"
            );

        yearElements.forEach(
            function (element) {

                element.textContent =
                    new Date().getFullYear();

            }
        );

    }
);


/* =========================================================
   23. SCROLL TO TOP
   ========================================================= */

function scrollToTop() {

    window.scrollTo({
        top: 0,
        behavior: "smooth"
    });

}


/* =========================================================
   24. CHARACTER COUNTER
   ========================================================= */

function setupCharacterCounter(
    inputId,
    counterId,
    maxLength
) {

    const input =
        document.getElementById(inputId);

    const counter =
        document.getElementById(counterId);

    if (!input || !counter) {
        return;
    }


    function updateCounter() {

        const length =
            input.value.length;

        counter.textContent =
            length + " / " + maxLength;

    }


    input.addEventListener(
        "input",
        updateCounter
    );

    updateCounter();

}


/* =========================================================
   25. INITIALIZE CHARACTER COUNTERS
   ========================================================= */

document.addEventListener(
    "DOMContentLoaded",
    function () {

        setupCharacterCounter(
            "description",
            "description-counter",
            500
        );

        setupCharacterCounter(
            "address",
            "address-counter",
            300
        );

    }
);