from pypdf import PdfReader
import dotenv
from boto3 import Session
from botocore.exceptions import BotoCoreError, ClientError
from contextlib import closing
import os
import sys

# Load Environment Variables
dotenv.load_dotenv()

# Constants and Files Directory
PDF_FILE = os.environ.get('PDF_FILE', False)


# you can use your PDF_FILE path here


def read_pdf(pdf_file_path: str) -> str:
    """
    Read PDF File and return text
    """
    reader = PdfReader(pdf_file_path)
    all_text_from_pages = ""
    for page in reader.pages:
        all_text_from_pages += page.extract_text()

    # for testing purposes
    return all_text_from_pages


def convert_to_speech(text: str):
    """
    Takes a text input and saves the output (mp3) in the same directory
    It uses AWS Polly to convert text to speech, en-GB, Arthur voice
    You can change the voice by changing the VoiceId parameter and other parameters.
    """
    # Loading AWS session variables from environment
    region = os.environ.get('AWS_REGION', False)
    aws_access_key_id = os.environ.get('ACCESS_KEY', False)
    aws_secret_key = os.environ.get('SECRET_ACCESS_KEY', False)

    session = Session(aws_access_key_id=aws_access_key_id, aws_secret_access_key=aws_secret_key, region_name=region)
    polly = session.client("polly")

    try:
        # Request speech synthesis
        response = polly.synthesize_speech(Engine="standard",
                                           LanguageCode="en-US",
                                           Text=text,
                                           OutputFormat="mp3",
                                           VoiceId="Joanna")
    except (BotoCoreError, ClientError) as error:
        # The service returned an error, exit gracefully
        print(error)
        sys.exit(-1)

    # Access the audio stream from the response
    if "AudioStream" in response:
        # Note: Closing the stream is important because the service throttles on the
        # number of parallel connections. Here we are using contextlib.closing to
        # ensure the close method of the stream object will be called automatically
        # at the end of the with statement's scope.
        with closing(response["AudioStream"]) as stream:
            output = "speech.mp3"

            try:
                # Open a file for writing the output as a binary stream
                with open(output, "wb") as file:
                    file.write(stream.read())
            except IOError as error:
                # Could not write to file, exit gracefully
                print(error)
                sys.exit(-1)

    else:
        # The response didn't contain audio data, exit gracefully
        print("Could not stream audio")
        sys.exit(-1)


def main():
    # get text from pdf file
    text = read_pdf(PDF_FILE)
    # convert text to speech
    convert_to_speech(text)


if __name__ == "__main__":
    main()