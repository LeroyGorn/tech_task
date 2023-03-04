let formRegex = RegExp(`form-(\\d){1}-`,'g');
let initialNode = document.querySelectorAll('#schema-row');

$(function(){

    $(document).on('change',"select[id$='column_type']", function(){
        let e = $(this);
        let selected_value = e.val()
        let selected_id = e.attr("id")
        selected_id = selected_id.replace ( /[^\d.]/g, '' );

        let to_value = document.querySelector(`#id_form-${selected_id}-to_value`);
        let from_value = document.querySelector(`#id_form-${selected_id}-from_value`);

        if (selected_value == 'Integer'){
            to_value.removeAttribute('disabled');
            from_value.removeAttribute('disabled');
            to_value.removeAttribute('placeholder');
            from_value.removeAttribute('placeholder');
        }else if (selected_value == 'Text'){
            to_value.removeAttribute('disabled');
            from_value.removeAttribute('disabled');
            to_value.setAttribute('placeholder', 'Sentences');
            from_value.setAttribute('placeholder', 'Sentences');
        }else{
            to_value.setAttribute('disabled', 'disabled');
            from_value.setAttribute('disabled', 'disabled');
        }
    });

    $(document).on('click','.btn-add', function(event){
        let copyNode = document.querySelectorAll('#schema-row');
        let table = $("#form_table > tbody")
        var collectionHolder = $('#form_schemas');
        var index = copyNode.length;

        let form = copyNode;
        let totalForms = document.querySelector(`#id_form-TOTAL_FORMS`);
        let newForm = '';
        if (index == 1){
            let in_form = initialNode;
            newForm = in_form[in_form.length - 1].cloneNode(true);
            var lastRow = collectionHolder.find('tr[id^="schema-row"]').last();
            lastRow.after(newForm);

        }else if (index != 0){
            newForm = form[form.length - 1].cloneNode(true);
            newForm.innerHTML = newForm.innerHTML.replace(formRegex, `form-${index}-`);
            var lastRow = collectionHolder.find('tr[id^="schema-row"]').last();
            lastRow.after(newForm);
        }else{
            let in_form = initialNode;
            newForm = in_form[in_form.length - 1].cloneNode(true);
            newForm.innerHTML = newForm.innerHTML.replace(formRegex, `form-${index}-`);
            table.append(newForm);
        }

        totalForms.setAttribute('value', `${index + 1}`)
        let formsNumber = index + 1;
        let schem = copyNode;
        for (let i = 0; i < formsNumber; i++) {
            let indexes = $(schem[i]).find(':input');
            let prefix = `form`
            indexes.each(function () {
                updateElementIndex(this, prefix, i);
            });
        }
        event.preventDefault();
    });

});

function removeSchema(holder) {
    holder = $(holder).closest('tr');
    holder.remove();

    let copyNode = document.querySelectorAll('#schema-row');

    let index = copyNode.length - 1;
    let totalForms = document.querySelector(`#id_form-TOTAL_FORMS`);
    totalForms.setAttribute('value', `${index}`);

    let formsNumber = copyNode.length + 1;
    let schem = copyNode;
    for (let i = 0; i < formsNumber; i++) {
        let indexes = $(schem[i]).find(':input');
        let prefix = `form`
        indexes.each(function () {
            updateElementIndex(this, prefix, i);
        });
    }
};

function updateElementIndex(el, prefix, ndx) {
    var id_regex = new RegExp('(' + prefix + '-\\d+)');
    var replacement = prefix + '-' + ndx;
    if ($(el).attr("for")) $(el).attr("for", $(el).attr("for").replace(id_regex, replacement));
    if (el.id) el.id = el.id.replace(id_regex, replacement);
    if (el.name) el.name = el.name.replace(id_regex, replacement);
}
