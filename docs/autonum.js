function autonum(i, class_element, prefix) {
    $('.' + class_element).each(function (index) {
        var local_index = index + 1;
        $(this).html(prefix+i+"."+local_index);
    });
}

$(function() {
    autonum(numlab, "autosection", "");
    autonum(numlab, "autotask", "Task ");
});