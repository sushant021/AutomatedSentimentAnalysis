import face_recognition
from PIL import Image, ImageDraw
import numpy as np
import tkinter 
from tkinter import messagebox 
from tkinter import filedialog

#browse file
def browse_file():
    #initiate tinker and hide window 
    main_win = tkinter.Tk() 
    main_win.withdraw()
    
    main_win.overrideredirect(True)
    main_win.geometry('0x0+0+0')
    
    main_win.deiconify()
    main_win.lift()
    main_win.focus_force()
    
    #open file selector 
    main_win.sourceFile = filedialog.askopenfilename(parent=main_win, initialdir= "/",
    title='Please select a directory')
    
    #close window after selection 
    main_win.destroy()
    
    #print path 
    return main_win.sourceFile

def train_model():
    # Load and train for Obama images
    obama_image = face_recognition.load_image_file("obama.jpg")
    obama_face_encoding = face_recognition.face_encodings(obama_image)[0]
    
    # Load and train for Trump images
    trump_image = face_recognition.load_image_file("trump.jpeg")
    trump_face_encoding = face_recognition.face_encodings(trump_image)[0]
    
    # Load and train for Bernie images
    bernie_image = face_recognition.load_image_file("bernie.jpg")
    bernie_face_encoding = face_recognition.face_encodings(bernie_image)[0]
    
    # Create arrays of known face encodings and their names
    known_face_encodings = [
        obama_face_encoding,
        trump_face_encoding,
        bernie_face_encoding,
    #   trudeau_face_encoding
    ]
    return known_face_encodings


def find_all_faces(unknown_image):
    known_face_encodings = train_model()
    known_face_names = [
    "Obama",
    "Trump",
    "Sanders",
    ]
    # Find all the faces and face encodings in the unknown image
    face_locations = face_recognition.face_locations(unknown_image)
    face_encodings = face_recognition.face_encodings(unknown_image, face_locations)
    # Convert the image to a PIL-format image so that we can draw on top of it with the Pillow library
    # See http://pillow.readthedocs.io/ for more about PIL/Pillow
    pil_image = Image.fromarray(unknown_image)
    # Create a Pillow ImageDraw Draw instance to draw with
    draw = ImageDraw.Draw(pil_image)
    # Loop through each face found in the unknown image
    for (top, right, bottom, left), face_encoding in zip(face_locations, face_encodings):
        # See if the face is a match for the known face(s)
        matches = face_recognition.compare_faces(known_face_encodings, face_encoding)
    
        name = "Unknown"
    
        # If a match was found in known_face_encodings, just use the first one.
        # if True in matches:
        #     first_match_index = matches.index(True)
        #     name = known_face_names[first_match_index]
    
        # Or instead, use the known face with the smallest distance to the new face
        face_distances = face_recognition.face_distance(known_face_encodings, face_encoding)
        best_match_index = np.argmin(face_distances)
        names = []
        if matches[best_match_index]:
            name = known_face_names[best_match_index]
            names.append(name)
        
    
    #     Draw a box around the face using the Pillow module
        draw.rectangle(((left, top), (right, bottom)), outline=(0, 0, 255))
    
    #     Draw a label with a name below the face
        text_width, text_height = draw.textsize(name)
        draw.rectangle(((left, bottom - text_height - 10), (right, bottom)), fill=(0, 0, 255), outline=(0, 0, 255))
        draw.text((left + 6, bottom - text_height - 5), name, fill=(255, 255, 255, 255))

    # Remove the drawing library from memory as per the Pillow docs
    del draw
    
    # Display the resulting image
    pil_image.show()
    
    
    # You can also save a copy of the new image to disk if you want by uncommenting this line
    # pil_image.save("image_with_boxes.jpg")
    
    # return the names of found faces 
    return names
    
    
# Load the image file for recognition
file_path = browse_file()
unknown_image = face_recognition.load_image_file(file_path)
names = find_all_faces(unknown_image)