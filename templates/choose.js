function choose(el) {
    element = document.getElementByClassName("friend");
    for (let i = 0; i < len(element); i++) {
        if (element[i].classList.contains("selected")) {
            element[i].classList.remove("selected")
        }
    }

    el.classList.add("selected");
}