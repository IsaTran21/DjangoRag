import drawChart from "./evaluation.js";
const form = document.getElementById("upload_form");
const uploadedInfo = document.getElementById("uploaded-info");
let evalDiv = document.getElementsByClassName('eval')

let getDone = 0;
let replyCount = 0;
const uploadedDone = document.getElementById("submit-button");
// For the Evaluation
let dataLine = [{
  x: [],
  y: [],
  mode: "lines",
  type: "scatter",

}];
let maxInTokens = 0;

// This is for the total input tokens details
let dataBarTotal = [{
        x: ["Total Input Tokens", "Total Output Tokens"],
        y: [0, 0],
        
        type: 'bar',
        orientation:"v",
        marker: {color:['orange', 'blue']},
        text: [0, 0],
        textposition: 'auto'
        }];
function generateSessionID() {
    return 'djangorag.' + Math.random().toString(36).substr(2, 9);
}

const sessionID = generateSessionID();

document.addEventListener('DOMContentLoaded', function() {
    
    
    async function uploadFile(){
        const formData = new FormData(form);
        formData.append("sessionID", sessionID);
        let response = await fetch('/api/files', {
                            method: 'POST',
                            body: formData,
                            headers: {
                                "X-CSRFToken": document.querySelector('[name=csrfmiddlewaretoken]').value
                            }
                        })
        return response
        
        }
    const submitForm = document.getElementById("submit-button");
    submitForm.addEventListener('click', (e)=>{
        e.preventDefault();
        getDone += 1;
        if (getDone < 2){
            uploadedDone.value = "Uploading...";
            uploadFile().then((response)=>{
            console.log("Just post");
            return response.json()})
        .then((result)=>{
        console.log("This is the response", result)
        console.log(`You just uploaded ${result["num_files"]} files`)
        
        uploadedDone.value = "Done";
        const fileInput = document.querySelector('input[name="pdf_files"]');
        const files = fileInput.files;

        let cheer;
        const br1 = document.createElement('br');
        if (files.length === 1){
        cheer = document.createTextNode(`${files.length} file is uploaded 🙂.`)}
        else if (files.length > 1){
        cheer = document.createTextNode(`${files.length} files are uploaded 🙂.`)}
        uploadedInfo.appendChild(cheer);
        uploadedInfo.appendChild(br1);
        const totalUploadPages = document.createTextNode(`There are total ${result["total_parsed_pages"]} pages being parsed using ${result["parse_method"]}🤩`);
        uploadedInfo.appendChild(totalUploadPages);
        const br2 = document.createElement('br');
        uploadedInfo.appendChild(br2);
        for (let file of files){
            let fileNameSlice;
            let fileName;
            if (file.name.length >= 20){
                fileNameSlice = file.name.substring(0, 20);
                fileName = document.createTextNode(`${fileNameSlice}...`)
            }
            else {
                fileNameSlice = file.name;
                fileName = document.createTextNode(`${fileNameSlice}`)
            }
            
            
            uploadedInfo.appendChild(fileName);
            const br = document.createElement('br');
            uploadedInfo.appendChild(br);
        }}
    ) // For then
    } // For if (getDone < 2)
    } // For addEventListener inner function
    )//for addEventListener

    let chatMessages = document.getElementById("chat-messages");
    let sendButton = document.getElementById("send-btn");
    let userMessage = document.getElementById("user-input");

    function getMessage(currentClassName, botMessage){
        if (currentClassName === "user"){
            let currentMessage = userMessage.value.trim()//remove spaces
            return currentMessage
            }
        if (currentClassName === "bot" && botMessage){
            let currentMessage = botMessage["response"];
            return currentMessage}
        };
    function sendMessage(currentClassName, botMessage){
        if (currentClassName === "user"){
            let currentUserMessage = getMessage(currentClassName, botMessage=botMessage)
            if (!currentUserMessage){
                console.log("Nothing to send");
            }
            else {
            let userTag = document.createElement("p");
            userTag.className = currentClassName;
            userTag.textContent = currentUserMessage;
            chatMessages.appendChild(userTag);}}
            // userMessage.value = "";
        if (currentClassName === "bot"){
            let currentBotMessage = getMessage(currentClassName, botMessage=botMessage)
            let botTag = document.createElement("p");
            botTag.className = currentClassName;
            botTag.textContent = currentBotMessage;
            chatMessages.appendChild(botTag);}}


    // For sending the message from the user to the bot endpoint :>
    async function sendMessageToBackend(){
 
        let currentUserMessage = userMessage.value.trim()//remove spaces
        userMessage.value="";
        console.log(`Current message ${currentUserMessage}`);
        if (currentUserMessage){
        const response = await fetch("/api/bot",{
                            method: 'POST',
                            headers: {
                            "Content-Type": "application/json",
                            },
                            body: JSON.stringify({ userText: currentUserMessage }),


        });
        const userText_ = await response.json();
        return userText_;
    }
    };
    sendButton.addEventListener("click", () => {
       
        sendButton.disabled = true;
        sendMessage("user");

        sendMessageToBackend()
            .then(botReply => {
                console.log("This is the bot reply:", botReply);
                sendMessage("bot", botReply);
                
                drawEvalCharts(botReply)
            })
            .catch(error => {
                console.error("Error from backend:", error);
            })
            .finally(() => {
                sendButton.disabled = false;
                userMessage.focus();
            });
    });
    // For the user to press enter when they are still in the 
    // input area to send the messsage instead of click the Send button.
    userMessage.addEventListener("keydown",
        (event)=>{
            
            
            if (event.key === "Enter"){
                // Prevent sending multiple times before the bot replies
                userMessage.disabled = true;
                sendMessage("user", undefined);
                
                sendMessageToBackend().then(botReply=>{     

                drawEvalCharts(botReply);
                sendMessage("bot", botReply);})
                .catch(error => {
                    console.log('error', error);
                })
                .finally(()=>{
                    userMessage.disabled = false;
                    userMessage.focus();
                })


                
            }
        }
    )
function drawEvalCharts(botReply){
        replyCount+=1;
        const inTokens = botReply['prompt_tokens'];
        const outTokens = botReply['output_tokens'];

        maxInTokens = maxInTokens > inTokens ? maxInTokens:inTokens;

        console.log(`This is is the maxInTokens ${maxInTokens}`);

        dataLine[0]['x'].push(replyCount);
        dataLine[0]['y'].push(inTokens);
        console.log("This is xLine and yLine", dataLine);

        let lineLayout = {
               title: {
                    text: 'Tokens usage over time'
                },
                // This is the key part for setting the range
                xaxis: {
                    title: {text: 'Prompt'}
                },
                yaxis: {
                    title: {text: 'Number of tokens'},
                    autorange: false,
                    range: [0, maxInTokens + 20] // Sets the y-axis to go from 0 to maxInTokens+ 20
                },

        };
        drawChart(evalDiv[0], dataLine, null, lineLayout);



        const dataPieCurrent = [{
                values: [inTokens, outTokens],
                labels: ["Input Tokens", "Output Tokens"],
                type: 'pie',
                // Combine 'value' and 'percent' flags
                textinfo: 'value+percent'
                }];
        drawChart(evalDiv[1], dataPieCurrent, "The details of current tokens usage")

        // The chart to total tokens usage so far
        dataBarTotal[0].y[0] += inTokens;
        dataBarTotal[0].y[1] += outTokens;


        dataBarTotal[0].text[0] += inTokens;
        dataBarTotal[0].text[1] += outTokens;
        let barLayout = {
            title: {
                text: 'Token usage'
            },
        };

        drawChart(evalDiv[2], dataBarTotal, null, barLayout)
}

});