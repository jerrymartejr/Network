document.addEventListener('DOMContentLoaded', function() {

    const buttons = document.querySelectorAll("button")
    for (const button of buttons) {
        button.addEventListener('click', () => {
            button.parentElement.style.display = 'none';
            button.parentElement.nextElementSibling.style.display = 'block';
        });
    }

    const edit_posts = document.querySelectorAll("#edit_post");
    for (const edit_post of edit_posts) {
        edit_post.style.display = 'none';
    }


    const saves = document.querySelectorAll("#save");
    for (const save of saves) {
        save.addEventListener('submit', (event) => {
            event.preventDefault();

            const body = save.edited_post.value;
            const post_id = parseInt(save.post_id.value);

            console.log(body);
            console.log(post_id);

            fetch('/edit_post', {
                method: "POST",
                body: JSON.stringify({
                    body: body,
                    post_id: post_id,
                    body: body
                })
            })
            .then(response => response.json())
            .then(result => {
                console.log(result);
                save.parentElement.previousElementSibling.firstElementChild.innerHTML = result.body;
            })

            save.parentElement.style.display = 'none';
            save.parentElement.previousElementSibling.style.display = 'block';

            return false;
        });
    }

    const likes = document.querySelectorAll("#like");
    for (const like of likes) {
        like.addEventListener('submit', (event) => {
            event.preventDefault();

            const post_id = parseInt(like.post_id.value);

            console.log(post_id);

            fetch('/like', {
                method: "POST",
                body: JSON.stringify({
                    post_id: post_id
                })
            })
            .then(response => response.json())
            .then(result => {
                console.log(result);
                like.previousElementSibling.innerHTML = result.num_likes;
            })

            like.lastElementChild.value = "Unlike";

            return false;
        });
    }

    const unlikes = document.querySelectorAll("#unlike");
    for (const unlike of unlikes) {
        unlike.addEventListener('submit', (event) => {
            event.preventDefault();

            const post_id = parseInt(unlike.post_id.value);

            console.log(post_id);

            fetch('/unlike', {
                method: "POST",
                body: JSON.stringify({
                    post_id: post_id
                })
            })
            .then(response => response.json())
            .then(result => {
                console.log(result);
                unlike.previousElementSibling.innerHTML = result.num_likes;
            })

            unlike.lastElementChild.value = "Like";

            return false;
        });
    }
});