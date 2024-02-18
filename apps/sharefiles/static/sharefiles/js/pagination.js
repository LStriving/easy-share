function showPageButton(data, currentPage) {
  var totalPages = parseInt(data.count / 10);
  if (data.count % 10) {
    totalPages += 1;
  }
  $(".pagination-links").empty();
  if (currentPage > 1) {
    $(".pagination-links").append(
      `<a href="?" class="w3-button pagination-link" page=${
        currentPage - 1
      }>&#10094; Previous</a>`
    );
  }
  if (currentPage < totalPages) {
    $(".pagination-links").append(
      `<a href="?" class="w3-button w3-right pagination-link" page=${
        currentPage + 1
      }>Next &#10095;</a>`
    );
  }
}
