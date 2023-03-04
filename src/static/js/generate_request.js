function generateCsv(){
    var btn = $(this);
    let rows_number = $('#rows_number').val();
    $('#generator_body tr').each(function() {
        let schema_id = $(this).find(".schema_id").html();
        let schema_status = $(this).find(".schema_status").html();

        if (schema_status == 'Not Generated') {
            $(this).find(".schema_status").html('Processing')
            let url = `/csv/?csv=false&file_id=${schema_id}&rows=${rows_number}`
            console.log(url)
            $.ajax({
                url: url,
                dataType: 'json',
                success: function (response) {
                    if (response.status == 'success') {
                        if (response.content.length > 0) {
                            $('.csv_table').html(response.content);
                        }
                    }
                }
            });
        }
    });
};
