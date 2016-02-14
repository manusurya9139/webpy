$(documents).ready(function(){
    activeTab('performance');
});
    
function activeTab(tab){
    $('.nav-tabs a[href="#' + tab + '"]').tab('show');
};

