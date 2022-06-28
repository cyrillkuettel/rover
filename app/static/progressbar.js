
const updateProgressBarEverySecond = (n)=>{
    let bar = document.getElementsByClassName("progress-bar")[0]

    for (let i = 1; i <= n; i++) {
        setTimeout( () =>{
        updateProgressBar(bar, i)
        }, i * 10)
      }
  }


function updateProgressBar(progressBar, value) {
    value = Math.round(value)
    
    progressBar.querySelector(".progress__fill").style.width = `${value}%`
    progressBar.querySelector(".progress__text__right").textContent = `${value}%`
}
