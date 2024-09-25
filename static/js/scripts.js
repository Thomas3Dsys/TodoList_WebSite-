
window.addEventListener('DOMContentLoaded', () => {
    let scrollPos = 0;
    const mainNav = document.getElementById('mainNav');
    const headerHeight = mainNav.clientHeight;
    window.addEventListener('scroll', function() {
        const currentTop = document.body.getBoundingClientRect().top * -1;
        if ( currentTop < scrollPos) {
            // Scrolling Up
            if (currentTop > 0 && mainNav.classList.contains('is-fixed')) {
                mainNav.classList.add('is-visible');
            } else {
                console.log(123);
                mainNav.classList.remove('is-visible', 'is-fixed');
            }
        } else {
            // Scrolling Down
            mainNav.classList.remove(['is-visible']);
            if (currentTop > headerHeight && !mainNav.classList.contains('is-fixed')) {
                mainNav.classList.add('is-fixed');
            }
        }
        scrollPos = currentTop;
    });

    
    const add_item_trigger_elements = document.getElementsByClassName('rename-item-input');
    for (var i = 0; i < add_item_trigger_elements.length; i++) {
        add_item_trigger_elements[i].addEventListener('change', addEditItemList, false);
        //add_item_trigger_elements[i].target_id= add_item_trigger_elements[i]["id"];
    }

})


const as= document.getElementsByClassName('rename-toggle-hidden');
const trigger = document.getElementById('rename_button');

trigger.addEventListener('click', () => {
  for( let r of as) 
  {
   r.classList.toggle('rename-toggle-shown')
  }
});


const modified_items = [];
const item_id_list = document.getElementById('item_id_list');
var addEditItemList = function() {
    modified_items.push(this.id)
};

const rename_submit_button = document.getElementById('rename-submit');
rename_submit_button.addEventListener('click', () => {
  item_id_list.value = modified_items.join(",");
  //  alert(item_id_list.value)
  form = document.getElementById('rename_form')
  form.submit();
});