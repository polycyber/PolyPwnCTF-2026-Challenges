import { Component, signal, Signal, WritableSignal } from '@angular/core';
import { HttpClient, HttpHeaders } from '@angular/common/http';
import { ReactiveFormsModule, FormBuilder, FormsModule, Form, FormGroup } from '@angular/forms';
import { catchError, firstValueFrom, of } from 'rxjs';

@Component({
  selector: 'app-profile-page',
  imports: [ReactiveFormsModule, FormsModule],
  templateUrl: './profile-page.html',
  styleUrl: './profile-page.css',
})
export class ProfilePage {

  profileForm: FormGroup;
  submissionSuccess: WritableSignal<boolean> = signal(false);
  submissionStatus: WritableSignal<string> = signal('');

  constructor(private http: HttpClient, private formBuilder: FormBuilder) {
      this.profileForm = this.formBuilder.group({
      mode: '',
      sequence_length: 0,
    });
  }
  
  async submitProfile() {
    this.submissionSuccess.set(false);
    console.log("Profile submitting: ", this.profileForm.value);
    if (!this.profileForm.value.mode || !this.profileForm.value.sequence_length) {
      this.submissionStatus.set('Both fields are required.');
      return;
    }

    // (mode: string, sequenceLength: number) {
    // Handle profile submission logic here
    // Send a POST request to the server with the profile data from the form in the HTML
      
        // const hostname = process.env.API_HOSTNAME; // Assuming you have set this in your environment
        // const hostname = "http://127.0.0.1";
        // const port = 3500;
        try {
          // const result = await firstValueFrom(this.http.get(`${hostname}/`).pipe(catchError((error) => {return of(undefined)})));
          const headers = new HttpHeaders({ 'Content-Type': 'application/json'});
          const result = await firstValueFrom(this.http.post(`api/set-mode/`, 
            { mode: this.profileForm.value.mode, length: this.profileForm.value.sequence_length }, { headers }).pipe(catchError((error) => {return of(undefined)}))
          );
          
          if (!result) {
            console.error("Error submitting profile");
            this.submissionSuccess.set(false);
            this.submissionStatus.set('Error submitting profile.');
            return;
          }
          console.log("Profile submission result: ", result);
          this.submissionSuccess.set(true);
          this.submissionStatus.set('Profile submitted successfully!');
        } catch (error) {
          console.error("Error submitting profile: ", error);
          this.submissionSuccess.set(false);
          this.submissionStatus.set('Error submitting profile.');
        }
      }


}
