// Used for Student/Teacher/Admin Page functions

// Tabs
const tabs = document.querySelectorAll('[data-tab-target]')
const tabsContent = document.querySelectorAll('[data-tab-content]') // Contains tabs content

// Loop through tabs
tabs.forEach(tab =>{
    // When specific tab is click, it'll run its content
    tab.addEventListener('click', () =>{
        // Grab tab element
        const target = document.querySelector(tab.dataset.tabTarget)

        tabsContent.forEach(tabsContent => {
            tabsContent.classList.remove('active')
        
        })
        // Loop over all over tab 
        tabs.forEach(tab => {
            tab.classList.remove('active')
        
        })
        // Display specific tab target when clicked  
        tab.classList.add('active')
        target.classList.add('active')
    })
})

// Add
// Remove 

