const openpopup = document.querySelectorAll("[data-profile-target]")
const closepopup = document.querySelectorAll("[data-close-button]")
const overlay = document.getElementById("overlay")
const openpdf = document.querySelectorAll("[data-preview-target]")
var previews = document.querySelectorAll("#preview")
const addsubjects = document.querySelectorAll("[data-addsub-target]")
const closeaddsub = document.querySelectorAll("[data-close-button]")
const closepdf = document.querySelectorAll("[data-closepdf-button]")
const remsubjects = document.querySelectorAll("[data-addsub-target]")
const closeremsub = document.querySelectorAll("[data-close-button]")
const uploadfile = document.querySelectorAll("[data-upload-target]")
const closeuploadfile = document.querySelectorAll("[data-close-button]")
var count = 0
//finish javascript copy paste add subjects

previews.forEach(preview => {
    preview.addEventListener("click",() => {
        previewstring = preview.value
        previewstringnew = previewstring.replace(/'/g, '"')
        const previewobj = JSON.parse(previewstringnew)
        console.log(previewobj)
        src = `${previewobj["filelink"]}`
        document.getElementById("preview-pdf").innerHTML = `
        <div id="preview-pdf-filename">
        </div>
        <embed id="preview-pdf-file" src="${src}">
        `     
    })
})
openpopup.forEach(button => {
    button.addEventListener("click",() => {
        const popup = document.querySelector(button.dataset.profileTarget)
        console.log(button.dataset)
        openpopupfunc(popup)
        console.log("Hello World")
    })
})
addsubjects.forEach(button => {
    button.addEventListener("click",() => {
        console.log(button.dataset)
        const addsubpopup = document.querySelector(button.dataset.addsubTarget)
        openpopupfunc(addsubpopup)
        console.log("Hello World")
    })
})  
remsubjects.forEach(button => {
    button.addEventListener("click",() => {
        console.log(button.dataset)
        const remsubpopup = document.querySelector(button.dataset.remsubTarget)
        openpopupfunc(remsubpopup)
        console.log("Hello World")
    })
}) 
uploadfile.forEach( button => {
    button.addEventListener('click',() => {
        const uploadpopup = document.querySelector(button.dataset.uploadTarget)
        openpopupfunc(uploadpopup)
    })
})
openpdf.forEach(button => {
    button.addEventListener("click",() => {
        const pdf = document.querySelector(button.dataset.previewTarget)
        console.log(button.dataset)
        openpopupfunc(pdf)
        console.log("Hello World")
    })
})
closepdf.forEach(button => {
    button.addEventListener("click",() => {
        const pdf = button.closest(".preview-pdf")
        document.getElementById("preview-pdf").innerHTML = ""
        closepopupfunc(pdf)
    })
})
closepopup.forEach(button => {
    button.addEventListener("click",() => {
        const popup = button.closest(".profile-open")
        closepopupfunc(popup)
    })
})
closeaddsub.forEach(button => {
    button.addEventListener("click",() => {
        const popup = button.closest(".addsub")
        popup.classList.remove("active")
        overlay.classList.remove("active")
    })
})
closeremsub.forEach(button => {
    button.addEventListener("click",() => {
        const popup = button.closest(".remsub")
        popup.classList.remove("active")
        overlay.classList.remove("active")
    })
})
closeuploadfile.forEach(button => {
    button.addEventListener("click",() => {
        const popup = button.closest(".uploadfile")
        popup.classList.remove("active")
        overlay.classList.remove("active")
    })
})
overlay.addEventListener('click', () => {
    const popups = document.querySelectorAll('.profile-open.active')
    const pdfs = document.querySelectorAll(".preview-pdf.active")
    document.getElementById("preview-pdf").innerHTML = ""
    popups.forEach(popup => {
      closepopupfunc(popup)
      
    })
    pdfs.forEach(pdf => {
        closepopupfunc(pdf)
    })
  })

function openpopupfunc(popup)
{
    if (popup == null ) return
    popup.classList.add("active")
    overlay.classList.add("active")
}
function closepopupfunc(popup)
{
    if (popup == null ) return
    popup.classList.remove("active")
    overlay.classList.remove("active")
}
function easteregg(){
    if (count < 7)
    {
        count += 1;
        console.log(count)
    }
    else{
        count = 0;
        window.open("/sharvil")
    }
}
